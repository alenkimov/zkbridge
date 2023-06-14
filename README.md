# zkBridge: zkNFT and zkMessenger
[ [Telegram канал](https://t.me/Cum_Insider) ]

- [О скрипте](#О-скрипте)
- [Запуск под Windows](#Запуск-под-Windows)
- [Запуск под Ubuntu](#Запуск-под-Ubuntu)


## О скрипте
Скрипт позволяет чеканить и бриджить случайно-сгенерированную NFT через [zkNFT](https://zkbridge.com/zknft), 
а также посылать случайное сообщение через [zkMessenger](https://zkbridge.com/zkmessenger)!

- Скрипт имеет графический интерфейс, написанный с помощью библиотеки [Dear PyGui](https://dearpygui.readthedocs.io/en/latest/index.html).
- Специально для работы с web3 и для этого скрипта из кусков чужого кода была собрана библиотека [better_web3](https://github.com/AlenKimov/better_web3).
- В консоль помимо базовой информации о происходящем выводятся ссылки на транзакции и количество потраченного газа.
- Лог сохраняется в папку `log`.
- RPC сетей хранятся в конфигурационном файле `config/chains.toml`.
- Генерация случайного изображение 100x100px и чеканка NFT стандарта ERC721 с помощью ZkBridgeCreator. Чеканка стандарта ERC1155 не реализована и реализована не будет.
- Запрос балансов кошельков перед совершением операции.


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


## Не реализовано
- [ ] Поддержка прокси
- [ ] Вывод диалогового окна с выбранными кошельками и их балансами перед совершением операции
- [ ] Кнопка "Открыть файл лога"
- [ ] Регистрация пользователя
- [ ] Ссылка хеша транзакции в консоли как кнопка, открывающая диалоговое окно, где можно скопировать хеш и открыть транзакцию в обозревателе
- [ ] Опциональное шифрование приватных ключей с установкой пароля
- [ ] Расчет и вывод приблизительных комиссий перед выполнением операции
- [ ] Установка максимальной цены газа для каждой сети
	- [ ] Ожидание установленной максимальной цены газа
- [ ] Установка газ-лимита для каждой сети
- [ ] Сохранение результатов работы в CSV таблицу
- Вкладка Chains
	- [ ] Изменение RPC сетей
	- [ ] Запрос актуальной цены газа
- Вкладка wallets
	- [ ] Удалить / Отключить все кошельки
	- [ ] Удалить / Отключить определенный кошелек
	- [ ] Флаг "показать приватные ключи"
	- [ ] Заголовок столбца — это кнопка, нажав на которую запрашиваются балансы кошельков