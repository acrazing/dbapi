const http = require('http')
http.createServer((req, res) => {
    const bufs = []
    req.on('data', buf => bufs.push(buf))
    req.on('end', () => {
        let raw = `${req.method} ${req.url} HTTP/${req.httpVersion}\r\n`
        raw += req.rawHeaders
            .filter((_, index) => index % 2 === 0)
            .map((item, index) => `${item}: ${req.rawHeaders[index * 2 + 1]}`)
            .join('\r\n')
        raw += '\r\n\r\n'
        raw += Buffer.concat(bufs).toString('utf8')
        console.log(raw)
        console.log('--')
        res.end(raw)
    })
}).listen(8000)