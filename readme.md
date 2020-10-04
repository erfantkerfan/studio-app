### Requirements
- running server of `rabbitmq`
- production server for uploading to
- local server for handling converting load
- custom `ffmpeg` build for supporting `libfdk_aac` and `libx264`
- web and sshpass installed
- keyscan cdn.alaatv.com >> ~/.ssh/known_hosts
---
### Running services - XXX refers to service name `convert`,`axis`,`upload`
```bash
sudo vim /lib/systemd/system/studio-XXX.service
sudo systemctl daemon-reload
sudo systemctl enable studio-XXX.service
sudo systemctl start studio-XXX.service
sudo systemctl restart studio-XXX.service
sudo systemctl status studio-XXX.service
sudo journalctl -f --no-pager -n 1000 --output=cat -u studio-XXX
```
---
### monitoring services log - XXX refers to service name `convert`,`axis`,`upload`,` `(*_empty_*) for watching all
```
./watch XXX
```
---
### Installation of clients
```
curl https://raw.githubusercontent.com/alaatv/studio-app/studio/install-app.bat > install.bat
```
then run the bat file