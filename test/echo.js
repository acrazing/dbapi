const http = require('http')
http.createServer((req, res) => {
    const bufs = []
    req.on('data', buf => bufs.push(buf))
    req.on('end', () => {
        res.end(JSON.stringify({url: req.url, headers: req.headers, body: Buffer.concat(bufs).toString('utf8')}))
    })
}).listen(8000)