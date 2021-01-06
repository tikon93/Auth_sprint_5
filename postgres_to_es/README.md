# Техническое задание
В предыдущем модуле вы реализовали механизм для для полнотекстового поиска. Теперь улучшим его: научим его работать 
с новой схемой и оптимизируем количество элементов для обновления.

# Подсказки к выполнению задания ETL

Здесь представлены все подсказки для работы создания ETL, которые могут быть полезны при выполнении задания:

1. Прежде, чем броситесь выполнять задание, подумайте, сколько ETL процессов вам нужно.
2. Для построения ETL процесса советуем использовать корутины, чтобы их попробовать на практике, так как в теме по 
асинхронности вы с ними столкнетесь опять.
3. Ваше приложение должно уметь восстанавливать контекст и начинать читать с того места, где оно закончило свою работу.
4. При конфигурировании ETL процесса продумайте, какие вам нужны параметры для запуска приложения. Старайтесь оставлять 
в коде как можно меньше "магических" значений.
5. (Желательно) Сделать составление запросов в БД максимально обобщенным, чтобы не пришлось постоянно дублировать код. 
При обобщении не забывайте про то, что все передаваемые значения в запросах должны экранироваться.
6. Использование тайпингов позволит сократить время дебага и понимание кода ревьюерами, а значит работы будут проверяться 
быстрее.
7. Обязательно пишите, что делают функции в коде.
8. Для логгирования используйте модуль `logging` из стандартной библиотеки Python.

Желаем удачи вам в написании ETL. Вы обязательно сможете осилить это!