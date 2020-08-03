import os
import random
import time
import urllib.request
import autoit

from selenium import webdriver


class InstagramBot:

    def __init__(self, username, password):
        self.username = username
        self.password = password

        # Указываем драйверу, что мы будем эмулировать андроид Galaxy S5
        mobile_emulation = {'deviceName': 'Galaxy S5'}
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)

        # Инициализируем драйвер
        self.browser = webdriver.Chrome(executable_path='chrome_driver/chrome_driver.exe', options=chrome_options)

        # Устанавливаем неявное ожидание
        self.browser.implicitly_wait(20)

    def login(self):
        try:
            # Устанавливаем размер окна браузера
            self.browser.set_window_size(360, 780)

            # Запускаем сайт инстаграм
            self.browser.get('https://instagram.com')

            # Нажимаем на кнопку входа
            self.browser.find_element_by_xpath(
                '/html/body/div[1]/section/main/article/div/div/div/div[2]/button').click()

            def enter_data():
                # Находим поля логин и пароль
                login_field = self.browser.find_element_by_name('username')
                password_field = self.browser.find_element_by_name('password')

                # Вводим логин
                login_field.clear()
                login_field.send_keys(self.username)

                # Вводим пароль
                password_field.clear()
                password_field.send_keys(self.password)

                # Подтверждаем вход
                password_field.submit()

            enter_data()

            try:
                # Проверяем не просят ли нас подождать некоторое время перед тем как повторно ввести данные(иногда
                # бывает), если нет, то идём дальше, если же просят ждём 4 секунды и вводим данные повторно
                self.browser.find_element_by_id('slfErrorAlert')
                time.sleep(4)
                enter_data()
            except:
                print('Вы вошли, без проблем')

        except Exception as ex:
            print(ex)
            self.exit()

    def exit(self):
        # Закрываем вкладку
        self.browser.close()
        # Закрываем браузер
        self.browser.quit()

    def get_posts_by_tag(self, tag, scroll_times=0, posts_number=0):
        try:
            # Переходим на страницу публикаций с указаным тегом
            self.browser.get(f'https://www.instagram.com/explore/tags/{tag}')

            # Прокручиваем страницу вниз заданое кол-во раз
            for times in range(scroll_times):
                self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')

            # Находим все теги ссылки
            posts = self.browser.find_elements_by_tag_name('a')

            # Выбираем из тегов ссылок, только ссылки на посты
            posts_links = [el.get_attribute('href') for el in posts if '/p/' in el.get_attribute('href')]

            # Отдаем список ссылок на посты
            return posts_links[:posts_number] if posts_number > 0 else posts_links

        except Exception as ex:
            print(ex)
            self.exit()

    def like_posts(self, urls, delay_range=None):
        try:
            # Устанавливаем задержку по умолчанию, если не была передана
            if delay_range is None:
                delay_range = [60, 120]

            # Проходимся по всем заданым постам и ставим лайки(с задержкой)
            for url in urls:
                # Переходим по ссылке на пост
                self.browser.get(url)

                # Ставим лайк посту
                self.browser.find_element_by_xpath(
                    '/html/body/div[1]/section/main/div/div[1]/article/div/div[3]/section[1]/span[1]/button').click()

                # Засыпаем
                time.sleep(random.randrange(delay_range[0], delay_range[1]))

        except Exception as ex:
            print(ex)
            self.exit()

    def download_posts(self, *urls):
        def download_post(post_type):
            # Определяем директории, в зависимости от типа ресурса
            if post_type == 'img':
                res_number_dir = 'posts/img_number.txt'
            else:
                res_number_dir = 'posts/video_number.txt'

            # Считываем с файла какой по счету скачиваемый ресурс
            with open(res_number_dir) as file:
                res_number = int(file.readline())

            # Определяем директории, в зависимости от типа ресурса
            if post_type == 'img':
                res_output_dir = f'posts/img/img_{res_number}.jpg'
            else:
                res_output_dir = f'posts/video/video_{res_number}.mp4'

            # Скачиваем ресурс по ссылке, которую получили выше
            urllib.request.urlretrieve(res_url, res_output_dir)

            # Увеличиваем номер ресурса для следующего скачивания
            with open(res_number_dir, 'w') as file:
                res_number += 1
                file.write(str(res_number))

        try:
            # Переходим на посты по ссылкам, которые получаем как параметр urls и скачиваем ресурс поста
            for url in urls:
                # Переходим по ссылке поста
                self.browser.get(url)

                # Проверяем тип ресурса(изображение или видео), если ресурсом поста будет изображние, то сработает
                # блок try, если видео, то блок except, если исключение, то блок except, который находится
                # внутри except
                try:
                    res_url = self.browser.find_element_by_class_name('tWeCl').get_attribute('src')
                    download_post('video')
                except Exception as ex:
                    print(ex)

                    try:
                        res_url = self.browser.find_element_by_class_name('FFVAD').get_attribute('src')
                        download_post('img')
                    except Exception as ex:
                        print(ex)
                        self.exit()

        except Exception as ex:
            print(ex)
            self.exit()

    @staticmethod
    def reset_download_posts():
        # Функция для сброса числа в файле до 1
        def reset_values(path):
            with open(path, 'w') as file:
                file.write('1')

        # Функция для удаления всех файлов в директории
        def delete_files(path):
            folder = os.listdir(path)
            for file in folder:
                os.remove(os.path.join(path, file))

        reset_values('posts/img_number.txt')
        reset_values('posts/video_number.txt')
        delete_files('posts\\img')
        delete_files('posts\\video')

    def publish_post(self, file_path, description=''):
        # Обходим попап переходом на вкладку поиска
        self.browser.get('https://www.instagram.com/explore/')

        # Нажимаем на кнопку добавления поста
        self.browser.find_element_by_xpath(
            '/html/body/div[1]/section/nav[2]/div/div/div[2]/div/div/div[3]').click()

        # Указываем расположение ресурса для нашего поста в сплывающем окне виндовс
        autoit.control_set_text('Открытие', 'Edit1', file_path)
        autoit.control_send('Открытие', 'Edit1', '{ENTER}')

        # Пропускаем кадрирование нашего ресурса
        self.browser.find_element_by_class_name('UP43G').click()

        # Заполняем описание и подтверждаем публикацию
        description_field = self.browser.find_element_by_tag_name('textarea')
        description_field.clear()
        description_field.send_keys(description)
        self.browser.find_element_by_class_name('UP43G').click()

        # Удаляем ресурс, который был использован для публикации
        os.remove(file_path)

    def publish_posts(self, description='', include_videos=False, posts_number=None, delay=None):
        try:
            # Выставляем пути к директориям
            img_folder_path = os.getcwd() + '\\posts\\img'
            video_folder_path = os.getcwd() + '\\posts\\video'

            # Публикуем только изображения
            if not include_videos:
                for res in os.listdir(img_folder_path):
                    res_path = img_folder_path + '\\' + res
                    self.publish_post(res_path, description=description)
                    time.sleep(delay)

            # Публикуем изображения и видео в перемешку(случайным образом)
            else:
                def publish_loop(posts_num):
                    for i in range(posts_num):
                        # Списки с видео и изображениями
                        img_files_list = os.listdir(img_folder_path)
                        video_files_list = os.listdir(video_folder_path)

                        # Кол-во изображений и видео всего
                        img_files_number = len(img_files_list)
                        video_files_number = len(video_files_list)

                        # Функция для публикации типа ресурса, указаного как параметр, где 0 - изображение,
                        # остальное(подразумевается 1) - видео
                        def select_resource_type(number):
                            if number == 0:
                                resource = img_files_list[random.randrange(0, img_files_number)]
                                resource_path = img_folder_path + '\\' + resource
                                self.publish_post(resource_path, description=description)
                                time.sleep(delay)
                            else:
                                resource = video_files_list[random.randrange(0, video_files_number)]
                                resource_path = video_folder_path + '\\' + resource
                                self.publish_post(resource_path, description=description)
                                time.sleep(delay)

                        # Публикуем файл(видео или изображения) случайным образом,при условии что есть файлы двух типов
                        if img_files_number > 0 and video_files_number > 0:
                            select_resource_type(random.randrange(0, 2))

                        # Публикуем только изображения, при условии что есть только изображения
                        elif img_files_number > 0 and video_files_number == 0:
                            select_resource_type(0)

                        # Публикуем только видео, при условии что есть только видео
                        elif img_files_number == 0 and video_files_number > 0:
                            select_resource_type(1)

                if posts_number is None:
                    # Кол-во всех файлов из директорий видео и фото
                    all_files_number = len(os.listdir(img_folder_path)) + len(os.listdir(video_folder_path))
                    # Публикуем все файлы, которые есть в директориях фото и видео
                    publish_loop(all_files_number)
                else:
                    # Публикуем указаное кол-во публикаций
                    publish_loop(posts_number)

        except Exception as ex:
            print(ex)
            self.exit()

    def __del__(self):
        print('Работа окончена, удачи)')
