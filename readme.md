### Requirements
- running server of `rabbitmq`
- production server for uploading to
- local server for handling converting load
- custom `ffmpeg` build for supporting `libfdk_aac` and `libx264`
- web and sshpass installed
- ssh-keyscan cdn.alaatv.com >> ~/.ssh/known_hosts
- `sudo apt install supervisor`
---
### Running supervisor - XXX refers to supervisor name `convert`,`axis`,`upload`
```bash
sudo vim /etc/supervisor/conf.d/studio-XXX.conf
sudo supervisorctl reread
sudo supervisorctl update
```
---
### Installation of clients
```
curl https://raw.githubusercontent.com/erfantkerfan/studio-app/master/install-app.bat > install.bat
```
then run the bat file