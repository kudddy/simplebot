## Подготовка образа

сборка образа
```
docker build -t docker.io/kudddy/gantlg .
```

загрузка образа
```
docker push docker.io/kudddy/gantlg:latest
```

генерация config map
```
kubectl create configmap anime-gan-test  --from-file=prod.yaml  --output yaml
```

Rolling Update

```
kubectl set image deployments/gan-tlg-deployment gantlg=kudddy/gantlg
```

docker tag
```
docker tag bf1fc6eaefcb docker.io/kudddy/gantlg:release-01
```

docker push
```
docker push docker.io/kudddy/gantlg:release-01
```

запрос для расчета статистики

```
select date_trunc('day', date) as time, count(user_id) from user_audit_gan

group by time

order by time desc
```