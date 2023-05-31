# zkBridge NFT mint, bridge, claim
[ [Channel](https://t.me/Cum_Insider) ]

- [Запуск под Windows](#Запуск-под-Windows)
- [Запуск под Ubuntu](#Запуск-под-Ubuntu)
- [Работа со скриптом](#Работа-со-скриптом)


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
    poetry update
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
poetry update
```
- Запустите скрипт:
```bash
poetry run python start.py
```


## Работа со скриптом
После первого запуска будет создан файл `private_keys.txt` в папке `input`.
Внесите приватные ключи (не сид-фраза) в этот файл.

Некоторые параметры бота можно настроить в файле `config/config.toml`.
