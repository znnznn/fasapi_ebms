import * as fs from 'fs'
import * as http from 'http'
import * as path from 'path'
import { fileURLToPath } from 'url'

const server = http.createServer((req, res) => {
    const __filename = fileURLToPath(import.meta.url)
    const __dirname = path.dirname(__filename)

    const filePath = path.join(
        __dirname,
        'dist',
        req.url === '/' ? 'index.html' : req.url
    )
    const contentType = getContentType(filePath)

    fs.readFile(filePath, (err, content) => {
        if (err) {
            if (err.code === 'ENOENT') {
                res.writeHead(404)
                res.end('File not found')
            } else {
                res.writeHead(500)
                res.end('Server error')
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType })
            res.end(content, 'utf-8')
        }
    })
})

server.listen(3000)

function getContentType(filePath) {
    const extname = path.extname(filePath)
    switch (extname) {
        case '.html':
            return 'text/html'
        case '.css':
            return 'text/css'
        case '.js':
            return 'text/javascript'
        case '.json':
            return 'application/json'
        default:
            return 'application/octet-stream'
    }
}
