
# people_database
A database with the opportunity to adding people and reviews to them and Telegram bot  
Consist of 2 tables:  
- Table 1:    
  - id,  
  - first_name,  
  - surname,  
  - biography  
- Table 2:  
  - id,  
  - review,  
  - person_id  

The DBMS of this project is the MySQL. To create a database input the following command into the sql file:  
CREATE DATABASE your_database_name;  
In my example:  
CREATE DATABASE people;  

To install a necessary python modules input:  
pip install -r requirements.txt    
  
#######################################################  
    
База данных с возможностью добавления людей и отзывов к ним и телеграмм бот

Используемая СУБД - MySQL. Для создания базы данных введите следующую команду в sql файл:
CREATE DATABASE your_database_name;
В моем случае:
CREATE DATABASE people;

Для установки необходимых python модулей введите:
pip install PyMySQL, PyTelegramBotAPI
