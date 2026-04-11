const net = require('net');
const mineflayer = require('mineflayer');
const { spawn } = require('child_process');
const iconv = require('iconv-lite');
const fs = require('fs');
const path = require('path');
const archiver = require('archiver');
const unzipper = require('unzipper');

let isProcessing = false;

const deleteFolderRecursive = function (directoryPath) {
  if (fs.existsSync(directoryPath)) {
    fs.readdirSync(directoryPath).forEach((file, index) => {
      const curPath = path.join(directoryPath, file);
      if (fs.lstatSync(curPath).isDirectory()) {
        deleteFolderRecursive(curPath);
      } else {
        fs.unlinkSync(curPath);
      }
    });
    fs.rmdirSync(directoryPath);
  }
};

const server = net.createServer((socket) => {
  socket.on('data', (data) => {
    if (isProcessing) {
      console.log('Обработка уже идет. Подождите.');
      socket.write('Обработка уже идет. Подождите.');
      return;
    }

    socket.on('close', () => {
      console.log('Клиент закрыл соединение');
      isProcessing = false;
    });

    socket.on('error', (err) => {
      if (err.code === 'ECONNRESET') {
        console.log('Соединение было неожиданно закрыто клиентом');
      } else {
        console.error('Произошла ошибка:', err);
      }
      isProcessing = false;
    });

    isProcessing = true;
    const directoryPath = path.join(__dirname, 'cryptomine');
    deleteFolderRecursive(directoryPath);
    console.log(`Папка ${directoryPath} и все вложенные файлы и папки были успешно удалены.`);

    let message = data.toString().trim();
    let command, args;
    [command, root, ...args] = message.split(' ');
    const argsString = args.join(' ');
    if (command === 'decrypt') {
      fs.createReadStream('encrypted.zip')
        .pipe(unzipper.Extract({ path: 'cryptomine' }))
        .on('close', () => console.log('Архив распакован в папку "cryptomine".'));
    }
    if (command === 'encrypt' || command === 'decrypt') {
      const minecraftProcess = spawn('java', [
        '-Xms1024M',
        '-Xmx1024M',
        '-Dfile.encoding=CP1251',
        '-jar',
        '-DIReallyKnowWhatIAmDoingISwear',
        'craftbukkit.jar'
      ]);

      minecraftProcess.stdout.on('data', (data) => {
        console.log(iconv.decode(data, 'win1251').toString());
      });

      const startBotAndScript = () => {
        const bot = mineflayer.createBot({
          host: 'localhost',
          username: 'Bot'
        });

        bot.once('spawn', () => {
          const pythonProcess = spawn('python3', ['./bot.py', command, root, argsString]);
          console.log(iconv.decode(data, 'utf-8').toString());
          if (command === 'decrypt') {
            pythonProcess.stdout.on('data', (data) => {
              const result = iconv.decode(data, 'win1251').toString();
              console.log(result);
              socket.write(result, () => {
                socket.end();
              });
            });
          }
          pythonProcess.stderr.on('data', (data) => {
            console.error(iconv.decode(data, 'win1251').toString());
          });

          pythonProcess.on('close', (code) => {
            bot.chat('/stop');
            if (command === 'encrypt') {
              setTimeout(() => {
                const archive = archiver('zip', {
                  zlib: { level: 9 }
                });

                const directoryPath = path.join(__dirname, 'cryptomine');
                const outputPath = path.join(__dirname, 'decryptmine.zip');
                const output = fs.createWriteStream(outputPath);
                output.on('close', function () {
                  console.log(archive.pointer() + ' total bytes');
                  console.log('Архиватор сообщил о завершении архивации и готовности потока вывода');

                  const fileContent = fs.readFileSync(outputPath);
                  socket.write(fileContent, () => {
                    socket.end();
                  });
                });

                archive.on('error', function (err) {
                  throw err;
                });

                archive.pipe(output);

                archive.directory(directoryPath, false);

                archive.finalize();
              }, 5000);
            };
            isProcessing = false;
          });
        });
      };

      setTimeout(startBotAndScript, 15000);
    } else {
      console.log('Неизвестная команда: ' + command);
      socket.write('Неизвестная команда: ' + command, () => {
        socket.end();
      });
      isProcessing = false;
    }
  });
});

server.listen(10020, '0.0.0.0', () => {
  console.log('Сервер запущен на порту 10020 (IPv4)');
});