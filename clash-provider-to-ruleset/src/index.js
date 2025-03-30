import jsyaml from 'js-yaml';

// 工具函数：解码 URL
function decodeUrl(encodedUrl) {
    try {
        return decodeURIComponent(encodedUrl);
    } catch (e) {
        return null;
    }
}

// 工具函数：检查是否为 IPv4 地址
function isIPv4(ip) {
    const ipv4Pattern = /^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(\/(\d|[1-2]\d|3[0-2]))?$/;
    return ipv4Pattern.test(ip);
}

// 工具函数：检查是否为 IPv6 地址
function isIPv6(ip) {
    const ipv6Pattern = /^([\da-fA-F]{1,4}:){6}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^::([\da-fA-F]{1,4}:){0,4}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^([\da-fA-F]{1,4}:):([\da-fA-F]{1,4}:){0,3}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^([\da-fA-F]{1,4}:){2}:([\da-fA-F]{1,4}:){0,2}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^([\da-fA-F]{1,4}:){3}:([\da-fA-F]{1,4}:){0,1}((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^([\da-fA-F]{1,4}:){4}:((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^([\da-fA-F]{1,4}:){7}[\da-fA-F]{1,4}(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^:((:[\da-fA-F]{1,4}){1,6}|:)(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^[\da-fA-F]{1,4}:((:[\da-fA-F]{1,4}){1,5}|:)(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^([\da-fA-F]{1,4}:){2}((:[\da-fA-F]{1,4}){1,4}|:)(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^([\da-fA-F]{1,4}:){3}((:[\da-fA-F]{1,4}){1,3}|:)(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^([\da-fA-F]{1,4}:){4}((:[\da-fA-F]{1,4}){1,2}|:)(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^([\da-fA-F]{1,4}:){5}:([\da-fA-F]{1,4})?(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$|^([\da-fA-F]{1,4}:){6}:(\/([1-9]?\d|(1([0-1]\d|2[0-8]))))?$/;
    return ipv6Pattern.test(ip);
}

// 工具函数：转换为 classical 格式
function convertToClassicalFormat(rule) {
    if (rule.includes(',')) {
        return rule;
    }

    if (isIPv4(rule)) {
        return `IP-CIDR,${rule}`;
    } else if (isIPv6(rule)) {
        return `IP-CIDR6,${rule}`;
    } else {
        return `DOMAIN-REGEX,${rule}`;
    }
}

// 工具函数：处理 YAML 内容
function processYamlContent(content, convertToClassical = false) {
    try {
        const data = jsyaml.load(content);
        if (!data || !data.payload) {
            return null;
        }

        const rules = data.payload
            .filter(item => typeof item === 'string')
            .map(item => {
                return convertToClassical ? convertToClassicalFormat(item) : item;
            })
            .join('\n');

        return rules;
    } catch (e) {
        console.error('YAML parsing error:', e);
        return null;
    }
}

// 主处理函数
async function handleRequest(request) {
    try {
        // 获取 URL 参数
        const url = new URL(request.url);
        const encodedYamlUrl = url.pathname.slice(1); // 移除开头的斜杠
        const convertToClassical = (url.searchParams.get('convert') === 'false');

        // 解码 URL
        const yamlUrl = decodeUrl(encodedYamlUrl);
        if (!yamlUrl) {
            return new Response('Invalid URL', { status: 400 });
        }

        // 获取 YAML 内容
        const response = await fetch(yamlUrl);
        if (!response.ok) {
            return new Response('Failed to fetch YAML file', { status: response.status });
        }

        const yamlContent = await response.text();

        // 处理 YAML 内容
        const rules = processYamlContent(yamlContent, convertToClassical);
        if (!rules) {
            return new Response('Invalid YAML content', { status: 400 });
        }

        // 返回结果
        return new Response(rules, {
            headers: {
                'Content-Type': 'text/plain',
                'Content-Disposition': 'attachment; filename="rules.txt"'
            }
        });

    } catch (e) {
        console.error('Request handling error:', e);
        return new Response('Internal Server Error', { status: 500 });
    }
}

// 注册 Worker
addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request));
});