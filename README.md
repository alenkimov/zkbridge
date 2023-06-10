# zkBridge: zkNFT and zkMessenger
[ [Telegram канал](https://t.me/Cum_Insider) ]

- [Что делает скрипт](#Что-делает-скрипт)
- [Особенности скрипта](#Особенности-скрипта)
- [Запуск под Windows](#Запуск-под-Windows)
- [Запуск под Ubuntu](#Запуск-под-Ubuntu)
- [Работа со скриптом](#Работа-со-скриптом)
- [Настройка скрипта](#Настройка-скрипта)


## Что делает скрипт
Скрипт позволяет чеканить и бриджить NFT ([zkNFT](https://zkbridge.com/zknft)), 
а также общаться через [zkMessenger](https://zkbridge.com/zkmessenger)!

### zkNFT
- Пользователь выбирает две сети: сеть, в которой будет отчеканена NFT, 
и сеть, куда будет отправлена эта NFT. После этого пользователь нажимает кнопку `MINT and BRIDGE`.
- Запрос балансов загруженных в файл `input/private_keys.txt` кошельков.
- Генерация случайного изображение 100x100px и чеканка NFT с помощью ZkBridgeCreator.
- Бридж NFT из одной сети в другую.
- Ожидание 60 секунд и клейм NFT в целевой сети.

### zkMessanger
- Пользователь выбирает две сети: ...


## Особенности скрипта
- Скрипт имеет графический интерфейс, написанный с помощью библиотеки [Dear PyGui](https://dearpygui.readthedocs.io/en/latest/index.html).
- Специально для работы с web3 и для этого скрипта из кусков чужого кода была собрана библиотека [better_web3](https://github.com/AlenKimov/better_web3).
- В консоль помимо базовой информации о происходящем выводятся ссылки на транзакции и количество потраченного газа.
- Лог сохраняется в папку `log`.
- RPC сетей хранятся в конфигурационном файле `config/chains.toml`.
- Настройки приложения хранятся в файле `settings/settings.json`: их не нужно задавать каждый раз по новой.
- Чеканка NFT стандарта ERC721. Чеканка стандарта ERC1155 не реализована и реализована не будет.
- [ ] Установка максимального газа для каждой сети
- [ ] Расчет комиссий


## Запуск под Windows
- Установите [Python 3.11](https://www.python.org/downloads/windows/). Не забудьте поставить галочку напротив "Add Python to PATH".
- Установите пакетный менеджер [Poetry](https://python-poetry.org/docs/): [инструкция](https://teletype.in/@alenkimov/poetry).
- Установите MSVC и Пакет SDK для Windows: [инструкция](https://teletype.in/@alenkimov/web3-installation-error). Без этого при попытке установить библиотеку web3 будет возникать ошибка "Microsoft Visual C++ 14.0 or greater is required".
- Установите [git](https://git-scm.com/download/win). Это позволит с легкостью получать обновления скрипта командой `git pull`
- Откройте консоль в удобном месте...
  - Склонируйте (скачайте) этот репозиторий:
    ```bash
    git clone https://github.com/AlenKimov/zk_nft_bridge.git
    ```
  - Перейдите в папку проекта:
    ```bash
    cd zk_nft_bridge
    ```
  - Установите требуемые библиотеки следующей командой или запуском файла `install-libraries.bat`:
    ```bash
    poetry install
    ```
  - Запустите скрипт следующей командой или запуском файла `start.bat`:
    ```bash
    poetry run python start.py
    ```


## Запуск под Ubuntu
- Обновите систему:
```bash
sudo apt update && sudo apt upgrade -y
```
- Установите [git](https://git-scm.com/download/linux) и screen:
```bash
sudo apt install screen git -y
```
- Установите Python 3.11 и зависимости для библиотеки web3:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.11 python3.11-dev build-essential libssl-dev libffi-dev -y
ln -s /usr/bin/python3.11/usr/bin/python
```
- Установите [Poetry](https://python-poetry.org/docs/):
```bash
curl -sSL https://install.python-poetry.org | python -
export PATH="/root/.local/bin:$PATH"
```
- Склонируйте этот репозиторий:
```bash
git clone https://github.com/AlenKimov/zk_nft_bridge.git
```
- Перейдите в папку проекта:
```bash
cd zk_nft_bridge
```
- Установите требуемые библиотеки:
```bash
poetry install
```
- Запустите скрипт:
```bash
poetry run python start.py
```


## Работа со скриптом
После первого запуска будет создан файл `private_keys.txt` в папке `input`.
Внесите приватные ключи (не сид-фраза) в этот файл.


## Настройка скрипта
RPC сетей можно задать в файле `config/chains.toml`.
