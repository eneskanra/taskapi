
### Docker-Flask-Celery-MongoDB ile yapılmış proje yönetim uygulama API'si

#### (Mail bilgileri .env dosyasından güvenlik amaçlı kaldırılmıştır. Uygun mail bilgileri girilerek mail fonksiyonu aktif hale getirilebilir.)

Aşağıdaki komutları sırası ile çalıştırın.

#### Repoyu indirmek için
git clone https://github.com/eneskanra/taskapi.git

#### Konteynırları çalıştırın
cd taskapi
docker-compose up -d

#### env dosyasında bulunan mongodb root bilgileri ile giriş yaparak uygulamanın çalışacağı veritabanı ve kullanıcıları oluşturun
docker exec -it mongodb bash

mongo -u mongodbuser -p your_mongodb_root_password

use flaskdb

db.createUser({user: 'flaskuser', pwd: 'your_mongodb_password', roles: [{role: 'readWrite', db: 'flaskdb'}]})

exit

#### Yeni kullanıcı ile giriş yaparak kullanıcıyı aktif edin
mongo -u flaskuser -p your_mongodb_password --authenticationDatabase flaskdb

exit

exit

#### Postman ile API'leri test etmeye başlayabilirsiniz. 
#### Postman collection linki
https://www.getpostman.com/collections/f4e4dee04420c01ef504

#### User Register ve User Login işlemlerinden sonra diğer endpointler kullanılabilir.