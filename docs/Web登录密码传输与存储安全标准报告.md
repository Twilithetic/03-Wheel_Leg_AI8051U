# Web 登录密码传输与存储安全标准报告

> 📅 日期：2026年5月3日
> 📚 来源：OWASP Authentication Cheat Sheet、OWASP Password Storage Cheat Sheet、NIST SP 800-63B
> 👩‍🏫 整理：知心姐姐

---

## 一、核心问题

> 网页上登录用的密码是不是明文传给后端的？

**简短回答**：在 HTTPS 下，密码原文确实放在 HTTP 请求体里发给后端，但整个 TCP 连接被 TLS 全链路加密，中间人无法看到内容。服务器收到后立刻哈希比对，绝不存明文。

---

## 二、密码安全的"三段论"

密码安全分为三个独立环节，各司其职：

```
┌──────────────────────────────────────────────────────────────────┐
│                    密码的生命周期安全                               │
├──────────────┬──────────────────┬─────────────────────────────────┤
│ ① 传输中     │    ② 验证时       │    ③ 存储（At Rest）             │
│ (In Transit) │  (Verification)  │                                 │
├──────────────┼──────────────────┼─────────────────────────────────┤
│ HTTPS/TLS    │ 收到原始密码后    │ 数据库只存 bcrypt/Argon2id       │
│ 全链路加密    │ 立刻加盐哈希比对  │ 哈希值，绝不存明文！              │
│              │ 比完就丢弃原始密码 │ 每个用户独立随机盐（Salt）        │
└──────────────┴──────────────────┴─────────────────────────────────┘
```

---

## 三、传输层：HTTPS/TLS 加密

### 3.1 两种方式对比

| | HTTP（明文） | HTTPS/TLS（加密） |
|------|-------------|-----------------|
| 传输内容 | 全程明文可见 | 全链路加密 |
| 中间人攻击 | ✅ 可直接读取密码 | ❌ 只能看到乱码 |
| 服务器收到 | 原始密码 | 解密后的原始密码 |
| 是否安全 | ❌ 极其危险 | ✅ 业界标准 |

### 3.2 OWASP 官方规定

来自 [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)：

> **Transmit Passwords Only Over TLS or Other Strong Transport**
>
> The login page and all subsequent authenticated pages must be exclusively accessed over TLS or other strong transport. Failure to utilize TLS for the login page allows an attacker to modify the login form action, causing the user's credentials to be posted to an arbitrary location.

**翻译**：
1. 密码**只能**通过 TLS（HTTPS）传输
2. **登录页面本身**也必须走 HTTPS——否则攻击者可以篡改表单的 `action` 地址，让密码直接发到攻击者的服务器
3. 登录后**所有需要认证的页面**也必须走 HTTPS

### 3.3 额外安全措施：HSTS

**HSTS**（HTTP Strict Transport Security）是一个 HTTP 响应头，告诉浏览器"以后访问这个域名时，永远使用 HTTPS，不要尝试 HTTP"。

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

| 参数 | 作用 |
|------|------|
| `max-age` | 强制 HTTPS 的缓存时间（秒），推荐至少 1 年 |
| `includeSubDomains` | 子域名也强制 HTTPS |
| `preload` | 加入浏览器内置的 HSTS 预加载列表 |

### 3.4 TLS 版本要求

| TLS 版本 | 状态 | 说明 |
|---------|------|------|
| SSL 2.0 / 3.0 | ❌ 禁用 | 已废弃，存在严重漏洞 |
| TLS 1.0 / 1.1 | ❌ 禁用 | PCI DSS 已弃用 |
| **TLS 1.2** | ✅ 至少 | 最低要求 |
| **TLS 1.3** | ✅✅ 推荐 | 最新标准，握手更快更安全 |

---

## 四、验证流程：服务端收到密码后

```
步骤                    操作                           内存状态
─────────────────────────────────────────────────────────────
1. 收到 HTTPS 请求      解密 TLS，提取请求体           有原始密码
2. 查数据库             取出该用户的 salt 和 hash      有原始密码
3. 哈希计算             Argon2id(原始密码 + salt)      有原始密码
4. 比对                 计算结果 vs 存储的 hash         有原始密码
5. 判断                 匹配 → 登录成功                 有原始密码
6. 🔥 丢弃              立即从内存清除原始密码           无密码！
7. 返回                 200 OK + session cookie
```

**关键原则**：原始密码在服务器内存中的存在时间**越短越好**，绝不能被写入日志。

---

## 五、存储层：密码哈希算法

### 5.1 OWASP 推荐算法排序

来自 [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)：

| 优先级 | 算法 | 推荐配置 | 适用场景 |
|:--:|------|---------|---------|
| 🥇 | **Argon2id** | m=19456(19MiB), t=2, p=1 | 首选！2015 密码哈希竞赛冠军 |
| 🥈 | **scrypt** | N=2^17(128MiB), r=8, p=1 | Argon2id 不可用时的替代 |
| 🥉 | **bcrypt** | work factor ≥ 10 | 旧系统兼容（注意 72 字节限制） |
| ⚠️ | **PBKDF2** | 600,000+ 迭代(SHA-256) | 仅 FIPS-140 合规需要时使用 |

### 5.2 哈希 vs 加密

| | 哈希（Hashing） | 加密（Encryption） |
|------|--------------|-----------------|
| 方向 | **单向**，不可逆 | **双向**，可解密 |
| 适用 | 密码存储 ✅ | 需要读回原值的数据 |
| 被拖库后 | 无法还原原密码 | ❌ 可以被解密！ |
| 代表 | Argon2id, bcrypt | AES-256-GCM |

> ⚠️ **密码绝不能用加密（Encryption）存储！** 必须用专用的慢哈希算法（Argon2id/bcrypt）。

### 5.3 盐（Salt）和胡椒（Pepper）

```
                          盐 (Salt)          胡椒 (Pepper)
─────────────────────────────────────────────────────────────
性质                    每个用户唯一        全局共享
存储位置                和 hash 一起存       单独存放（HSM/密钥管理）
泄露影响                增加暴力破解难度     即使数据库泄露也无法破解
是否必需                ✅ 必需              ⚪ 可选（额外防御层）
```

**加盐后**：两个用户即使密码相同，哈希值也完全不同，无法用彩虹表批量破解。

### 5.4 为什么不推荐 MD5 / SHA-1 / SHA-256？

| 算法 | 设计目标 | 速度 | 适合密码？ |
|------|---------|------|:--:|
| MD5 | 数据完整性校验 | 极快 | ❌ |
| SHA-1 | 数据完整性校验 | 极快 | ❌ |
| SHA-256 | 数据完整性校验 | 快 | ❌ |
| bcrypt | **专门为密码设计** | 慢（可调） | ✅ |
| Argon2id | **专门为密码设计** | 慢（可调） | ✅✅ |

这些通用哈希算法**设计目标就是快**——GPU 每秒能算几十亿次，暴力破解易如反掌。而 bcrypt/Argon2id 故意做得慢，让暴力破解成本高到不可接受。

---

## 六、常见误区解答

### 误区 1："前端先用 JS hash 一下更安全"

```
❌ 错误做法：
  浏览器端: MD5("123456") = "e10adc..." → 发给后端

  问题：
  - "e10adc..." 变成了事实上的"密码"（Pass-the-Hash 攻击）
  - MD5/SHA256 是快速哈希，不是为密码安全设计的
  - HTTPS 已经把传输安全搞定了，不需要画蛇添足
```

**正确做法**：前端不做额外 hash，把原始密码放进 HTTPS 请求体即可。哈希的事交给服务端用 bcrypt/Argon2id。

### 误区 2："密码应该用 Base64 编码后传输"

Base64 是**编码**（Encoding），不是**加密**（Encryption）。任何人都能解码。这只是把二进制转成了可打印字符，对安全毫无帮助。

### 误区 3："登录接口不需要 HTTPS，后端存的时候用 bcrypt 就行"

❌ 大错特错！如果没有 HTTPS：
- 中间人可以窃听密码
- 中间人可以**修改登录表单的 `action`**，让密码直接发到攻击者服务器
- 中间人可以劫持 session cookie

**HTTPS 是在传输层保护密码，bcrypt 是在存储层保护密码，两者缺一不可！**

---

## 七、完整流程图

```
┌──────────────┐                                       ┌──────────────┐
│   浏览器      │         HTTPS (TLS 1.3)                │   服务器      │
│              │ ←══════════════════════════════════→  │              │
└──────┬───────┘                                       └──────┬───────┘
       │                                                      │
       │  POST /login                                         │
       │  Content-Type: application/json                      │
       │  Body: {"username":"baby",                           │
       │         "password":"my_pwd_123"}                     │
       │  (整个请求体被 TLS 加密！)                              │
       │ ────────────────────────────────────────────────→    │
       │                                                      │
       │                                              ┌───────▼────────┐
       │                                              │ 1. 解密 TLS    │
       │                                              │ 2. 提取密码     │
       │                                              │ 3. 查库取 salt  │
       │                                              │ 4. bcrypt(pwd  │
       │                                              │    + salt)     │
       │                                              │ 5. 比对 hash   │
       │                                              │ 6. 丢弃原密码   │
       │                                              └───────┬────────┘
       │                                                      │
       │  200 OK                                              │
       │  Set-Cookie: session_id=xxx;                         │
       │    Secure; HttpOnly; SameSite=Lax                    │
       │ ←────────────────────────────────────────────────   │
       │                                                      │
```

### Cookie 安全属性

| 属性 | 作用 |
|------|------|
| `Secure` | Cookie 只在 HTTPS 下发送 |
| `HttpOnly` | JS 无法读取 Cookie（防 XSS 窃取） |
| `SameSite=Lax` | 防止 CSRF 攻击 |
| `Max-Age` | 设置过期时间（不要用 `Expires`） |

---

## 八、标准和参考来源

| 标准/文档 | 全称 | 链接 |
|----------|------|------|
| OWASP Authentication Cheat Sheet | Web 认证安全标准 | [链接](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) |
| OWASP Password Storage Cheat Sheet | 密码存储标准 | [链接](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) |
| OWASP Transport Layer Security Cheat Sheet | TLS 配置标准 | [链接](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html) |
| OWASP ASVS | 应用安全验证标准 | [链接](https://owasp.org/www-project-application-security-verification-standard/) |
| NIST SP 800-63B | 美国数字身份验证标准 | [链接](https://pages.nist.gov/800-63-4/sp800-63b.html) |
| RFC 8446 | TLS 1.3 协议规范 | [链接](https://datatracker.ietf.org/doc/html/rfc8446) |
| PHC String Format | 密码哈希存储格式标准 | [链接](https://github.com/P-H-C/phc-string-format) |

---

## 九、一句话总结

> **传输靠 TLS，存储靠 Argon2id/bcrypt。前端不额外 hash，HTTPS 已经够了。密码在数据库里永远只存哈希值，而且每个用户独立加盐。**

---

*本报告由知心姐姐基于 OWASP 官方文档整理，供学习和参考使用 💕*
