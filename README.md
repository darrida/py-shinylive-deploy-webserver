shinylive export ./src_dev/app2 ./staging/app2 && rm -r ./src_test_webserver/shinyapps/app2 && mv ./staging/app2 ./src_test_webserver/shinyapps/

### Separate Commands
- Fresh deploy
```shell
shinylive export ./src_dev/app2 ./staging/app2
mv ./staging/app2 ./src_test_webserver/shinyapps/
```

- Redeploy
```shell
shinylive export ./src_dev/app2 ./staging/app2
rm -r ./src_test_webserver/shinyapps/app2
mv ./staging/app2 ./src_test_webserver/shinyapps/
```

### Single Commands
- Fresh deploy
```shell
shinylive export ./src_dev/app2 ./staging/app2 && \
mv ./staging/app2 ./src_test_webserver/shinyapps/
```

- Redeploy
```shell
shinylive export ./src_dev/app2 ./staging/app2 && \
rm -r ./src_test_webserver/shinyapps/app2 && \
mv ./staging/app2 ./src_test_webserver/shinyapps/
```

### SSH/SFTP/PSCP
- Copy directory and contents using Putty PSCP
```
pscp -r -i staging\app1\ user@host:/homes/user/docker_volumes/shinyapps/
```