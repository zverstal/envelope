import vk_api
from concurrent.futures import ThreadPoolExecutor, as_completed

# Функция для получения всех постов паблика
def get_all_posts(api, owner_id):
    posts = []
    offset = 0
    while True:
        # Получаем 100 постов за один запрос
        response = api.wall.get(owner_id=owner_id, offset=offset, count=100)
        posts += response['items']
        
        # Если вернулось меньше 100 постов, значит больше постов нет
        if len(response['items']) < 100:
            break
        offset += 100
    return posts

# Функция для получения всех комментариев к посту
def get_comments(api, owner_id, post_id):
    comments = []
    offset = 0
    total_comments = 0
    while True:
        # Получаем до 100 комментариев за один запрос
        response = api.wall.getComments(owner_id=owner_id, post_id=post_id, offset=offset, count=100)
        comments += response['items']
        total_comments += len(response['items'])  # Считаем количество комментариев
        
        # Если комментариев меньше 100, значит все комментарии загружены
        if len(response['items']) < 100:
            break
        offset += 100
    return comments, total_comments

# Функция для подсчета упоминаний слова "энвилоуп" в комментариях одного поста
def count_mentions_in_comments(api, owner_id, post, keyword):
    post_id = post['id']
    comments, total_comments = get_comments(api, owner_id, post_id)
    mention_count = 0
    
    # Проходим по всем комментариям и ищем упоминание ключевого слова с учётом регистра
    for comment in comments:
        if keyword in comment['text']:
            mention_count += 1
    
    return mention_count, total_comments

# Основная функция для подсчета упоминаний во всех комментариях с использованием многопоточности
def count_mentions_in_all_comments(api, owner_id, keyword):
    posts = get_all_posts(api, owner_id)  # Получаем все посты паблика
    total_posts = len(posts)  # Считаем количество постов
    total_comments = 0
    mention_count = 0
    
    # Используем ThreadPoolExecutor для многопоточности
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Создаем задачи для каждого поста
        futures = [executor.submit(count_mentions_in_comments, api, owner_id, post, keyword) for post in posts]
        
        # Обрабатываем результаты по мере завершения
        for future in as_completed(futures):
            post_mentions, post_comments = future.result()
            mention_count += post_mentions
            total_comments += post_comments
    
    return mention_count, total_posts, total_comments

if __name__ == '__main__':
    # Авторизация в API ВКонтакте с использованием токена
    vk_session = vk_api.VkApi(token='базара_джексон')  # Вставьте ваш токен
    vk = vk_session.get_api()
    
    owner_id = -218375169  # ID паблика, начинается с минуса для групп
    keyword = 'энвилоуп'  # Ищем слово именно с маленькой буквы
    
    # Подсчет упоминаний в комментариях
    mention_count, total_posts, total_comments = count_mentions_in_all_comments(vk, owner_id, keyword)
    
    # Вывод результата
    print(f'Слово "{keyword}" упоминается {mention_count} раз в комментариях к постам паблика.')
    print(f'Обработано {total_posts} постов и {total_comments} комментариев.')
