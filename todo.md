# ToDo List 

* Redesign readme.md for better readability
* Update issue templates

docker compose build --no-cache
docker compose up -d

docker compose exec database bash
mysql -uroot -p
tiger
CREATE DATABASE python;
exit
exit

docker compose exec webserver bash
cd /var/www/html

visit http://localhost


Task Description:
 1 Create a Python script that can load up to 100 YouTube channels from a text file or a database.
 2 The script should check for newly uploaded videos every X minutes.
 3 When a new video is detected on a channel, the script should choose a random preset comment text using spintax for that channel and post the comment using a preset YouTube account.
 4 The script should be able to retrieve the comment ID after posting the comment.
 5 After retrieving the comment ID, the script should send it to a third-party API to purchase comment likes (SMM panel).
 6 The script should be designed to be multithreaded, allowing simultaneous checks and actions to be performed on multiple channels without affecting each other.
 7 The script should have proxy support, allowing each YouTube account to be assigned a specific proxy.
Detailed Steps:
 1 Read channel URLs from a text file or a database.
 2 1.1. If using a text file, read line by line and store channel URLs in a list.
 3 1.2. If using a database, query the appropriate table and store channel URLs in a list.
 4 Create a function to check for newly uploaded videos.
 5 2.1. Scrape the channel's video page using a Python library (e.g., Beautiful Soup or Selenium).
 6 2.2. Parse the response to identify the latest video URL.
 7 2.3. Compare the latest video URL with the previously stored URL for that channel.
 8 2.4. If there is a new video, proceed to step 3; otherwise, wait for X minutes and repeat.
 9 Implement spintax for generating random preset comment texts.
 10 3.1. Parse the spintax string.
 11 3.2. Randomly select words or phrases from the parsed spintax.
 12 3.3. Generate the final comment text.
 13 Post the comment using the appropriate preset YouTube account.
 14 4.1. Log in to the YouTube account.
 15 4.2. Navigate to the new video page.
 16 4.3. Post the generated comment.
 17 Retrieve the comment ID.
 18 5.1. Locate the posted comment on the video page.
 19 5.2. Extract the comment ID from the comment element.
 20 Send the comment ID to the third-party API (SMM panel) to purchase comment likes.
 21 6.1. Create a function to send a POST request with the comment ID to the API endpoint.
 22 6.2. Handle the response from the API.
 23 Implement multithreading.
 24 7.1. Create a separate thread for each channel.
 25 7.2. Run the check for newly uploaded videos function within each thread.
 26 7.3. Ensure proper synchronization and error handling between threads.
 27 Add proxy support.
 28 8.1. Create a function to assign proxies to each YouTube account.
 29 8.2. Implement the proxy within the web scraping process.
 30 8.3. Ensure proper error handling and proxy switching if needed.

Опис завдання:
  1 Створіть сценарій Python, який може завантажити до 100 каналів YouTube із текстового файлу або бази даних.
  2 Сценарій має перевіряти наявність нещодавно завантажених відео кожні X хвилин.
  3 Коли на каналі виявлено нове відео, сценарій має вибрати випадковий попередньо встановлений текст коментаря 
    за допомогою spintax для цього каналу та опублікувати коментар за допомогою попередньо встановленого облікового запису YouTube.
  4 Сценарій повинен мати можливість отримати ідентифікатор коментаря після публікації коментаря.
  5 Після отримання ідентифікатора коментаря сценарій має надіслати його до стороннього API для придбання лайків 
    для коментарів (панель SMM).
  6 Сценарій має бути розроблений як багатопоточний, що дозволяє виконувати одночасні перевірки та дії на кількох каналах, 
    не впливаючи один на одного.
  7 Сценарій повинен підтримувати проксі-сервер, що дозволяє кожному обліковому запису YouTube призначати окремий проксі-сервер.
  Детальні кроки:
  1 Прочитайте URL-адреси каналів із текстового файлу чи бази даних.
  2 1.1. Якщо ви використовуєте текстовий файл, читайте рядок за рядком і зберігайте URL-адреси каналів у списку.
  3 1.2. Якщо ви використовуєте базу даних, надішліть запит до відповідної таблиці та збережіть URL-адреси каналів у списку.
  4 Створіть функцію для перевірки нових завантажених відео.
  5 2.1. Скопіюйте відеосторінку каналу за допомогою бібліотеки Python (наприклад, Beautiful Soup або Selenium).
  6 2.2. Проаналізуйте відповідь, щоб визначити URL-адресу останнього відео.
  7 2.3. Порівняйте URL-адресу останнього відео з попередньо збереженою URL-адресою для цього каналу.
  8 2.4. Якщо є нове відео, перейдіть до кроку 3; інакше зачекайте X хвилин і повторіть.
  9 Реалізуйте spintax для створення випадкових попередньо встановлених текстів коментарів.
  10 3.1. Проаналізуйте рядок spintax.
  11 3.2. Довільно виберіть слова або фрази з проаналізованого спінтаксу.
  12 3.3. Створіть остаточний текст коментаря.
  13 Опублікуйте коментар, використовуючи відповідний попередній обліковий запис YouTube.
  14 4.1. Увійдіть в обліковий запис YouTube.
  15 4.2. Перейдіть на сторінку нового відео.
  16 4.3. Опублікувати створений коментар.
  17 Отримайте ідентифікатор коментаря.
  18 5.1. Знайдіть опублікований коментар на сторінці відео.
  19 5.2. Витягніть ідентифікатор коментаря з елемента коментаря.
  20 Надішліть ідентифікатор коментаря в сторонній API (панель SMM), щоб придбати лайки для коментарів.
  21 6.1. Створіть функцію для надсилання запиту POST з ідентифікатором коментаря до кінцевої точки API.
  22 6.2. Обробляти відповідь від API.
  23 Реалізуйте багатопотоковість.
  24 7.1. Створіть окрему тему для кожного каналу.
  25 7.2. Запустіть функцію перевірки нещодавно завантажених відео в кожному потоці.
  26 7.3. Забезпечте належну синхронізацію та обробку помилок між потоками.
  27 Додати підтримку проксі.
  28 8.1. Створіть функцію призначення проксі для кожного облікового запису YouTube.
  29 8.2. Впровадьте проксі-сервер у процесі веб-збирання.
  30 8.3. Забезпечте належну обробку помилок і перемикання проксі-сервера, якщо необхідно.