rule-providers 文件内容

classical:

```yaml
payload:
- DOMAIN-SUFFIX,google.com
- DOMAIN-KEYWORD,google
- DOMAIN,ad.com
- SRC-IP-CIDR,192.168.1.201/32
- IP-CIDR,127.0.0.0/8
- GEOIP,CN
- DST-PORT,80
- SRC-PORT,7777
```

```text
DOMAIN-SUFFIX,google.com
DOMAIN-KEYWORD,google
DOMAIN,ad.com
SRC-IP-CIDR,192.168.1.201/32
IP-CIDR,127.0.0.0/8
GEOIP,CN
DST-PORT,80
SRC-PORT,7777
```

-------------------------

domain:

```yaml
payload:
- '.blogger.com'
- '*.*.microsoft.com'
- 'books.itunes.apple.com'
```

```text
.blogger.com
*.*.microsoft.com
books.itunes.apple.com
```

-------------------------------

ipcidr:

```yaml
payload:
- '192.168.1.0/24'
- '10.0.0.0.1/32'
```

```text
192.168.1.0/24
10.0.0.0.1/32
```