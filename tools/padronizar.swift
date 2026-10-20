// Padroniza uma foto de produto: quadrado 600x600, fundo branco, produto centralizado sem cortar.
// Uso: swift padronizar.swift entrada saida.jpg
import AppKit

let args = CommandLine.arguments
guard args.count == 3, let src = NSImage(contentsOfFile: args[1]),
      let rep = src.representations.first else { exit(1) }
let lado: CGFloat = 600, margem: CGFloat = 36
let w = CGFloat(rep.pixelsWide), h = CGFloat(rep.pixelsHigh)
let escala = min((lado - 2 * margem) / w, (lado - 2 * margem) / h)
let alvo = NSRect(x: (lado - w * escala) / 2, y: (lado - h * escala) / 2, width: w * escala, height: h * escala)

let bmp = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(lado), pixelsHigh: Int(lado),
                           bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                           colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: bmp)
NSGraphicsContext.current?.imageInterpolation = .high
NSColor.white.setFill()
NSRect(x: 0, y: 0, width: lado, height: lado).fill()
src.draw(in: alvo, from: .zero, operation: .sourceOver, fraction: 1)
NSGraphicsContext.restoreGraphicsState()
let jpg = bmp.representation(using: .jpeg, properties: [.compressionFactor: 0.78])!
try! jpg.write(to: URL(fileURLWithPath: args[2]))
