#!/bin/bash
# 🚀 Build WASM Discovery Engine

set -e

echo "======================================================================="
echo "🚀 Building WASM Infinite Discovery Engine"
echo "======================================================================="

# Check if wasm-pack is installed
if ! command -v wasm-pack &> /dev/null; then
    echo "❌ wasm-pack not found"
    echo "📦 Installing wasm-pack..."
    curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh
fi

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust not found"
    echo "📦 Install Rust from: https://rustup.rs/"
    exit 1
fi

echo ""
echo "✅ Prerequisites satisfied"
echo ""

# Navigate to Rust project
cd ../gitbank-rust

echo "🔧 Building WASM module with optimizations..."
echo ""

# Build with wasm-pack (enable wasm feature)
wasm-pack build --target web --out-dir ../wasm-web/pkg --release --features wasm

echo ""
echo "======================================================================="
echo "✅ WASM BUILD COMPLETE"
echo "======================================================================="
echo ""
echo "📁 Output: wasm-web/pkg/"
echo "📦 Package size:"
ls -lh ../wasm-web/pkg/gitbank_rust_bg.wasm | awk '{print "   " $5 " - " $9}'
echo ""
echo "🚀 Next steps:"
echo "   1. cd ../wasm-web"
echo "   2. python3 -m http.server 8080"
echo "   3. Open http://localhost:8080"
echo ""
echo "======================================================================="
