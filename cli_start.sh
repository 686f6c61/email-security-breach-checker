#!/bin/bash
# Email Security Breach Checker v2.0 - CLI Start Script

# Colores
ROJO='\033[0;31m'
VERDE='\033[0;32m'
AMARILLO='\033[1;33m'
AZUL='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${AZUL}[INFO]${NC} $1"; }
print_success() { echo -e "${VERDE}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${AMARILLO}[WARNING]${NC} $1"; }
print_error() { echo -e "${ROJO}[ERROR]${NC} $1"; }

check_python_version() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 no está instalado"
        echo "Instala Python 3.8+: sudo apt install python3 python3-pip python3-venv"
        exit 1
    fi
    
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_success "Python $PYTHON_VERSION detectado (✓)"
    else
        print_error "Se requiere Python 3.8+"
        exit 1
    fi
}

check_essential_files() {
    local files=("main.py" "requirements.txt" "src/" ".env.example")
    for file in "${files[@]}"; do
        if [ ! -e "$file" ]; then
            print_error "Archivo esencial faltante: $file"
            exit 1
        fi
    done
    print_success "Archivos esenciales verificados (✓)"
}

setup_virtual_environment() {
    if [ ! -d "venv" ]; then
        print_status "Creando entorno virtual..."
        python3 -m venv venv
        print_success "Entorno virtual creado (✓)"
    else
        print_success "Entorno virtual ya existe (✓)"
    fi
    
    source venv/bin/activate
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Entorno virtual activado (✓)"
    else
        print_error "Error al activar entorno virtual"
        exit 1
    fi
}

install_dependencies() {
    print_status "Instalando dependencias..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "Dependencias instaladas (✓)"
    else
        print_error "Error al instalar dependencias"
        exit 1
    fi
}

setup_configuration() {
    if [ ! -f ".env" ]; then
        print_warning "Archivo .env no encontrado"
        print_status "Creando .env desde .env.example..."
        cp .env.example .env
        print_success "Archivo .env creado (⚠️)"
        echo ""
        print_warning "IMPORTANTE: Edita .env con tus API keys"
        read -p "Presiona Enter para continuar..."
    else
        print_success "Archivo .env encontrado (✓)"
    fi
}

setup_directories() {
    local directories=("data/deposito" "data/generados" "cache" "logs")
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
        fi
    done
    
    if [ ! -f "data/deposito/emails_ejemplo.csv" ]; then
        cat > data/deposito/emails_ejemplo.csv << EOF
email
test@example.com
user@domain.com
admin@test.org
john.doe@company.net
jane.smith@email.co.uk
EOF
    fi
    
    print_success "Estructura de directorios verificada (✓)"
}

start_program() {
    print_status "Arrancando Email Security Breach Checker..."
    echo ""
    print_success "¡Todo listo! El programa está configurado."
    echo ""
    python3 main.py
}

main() {
    echo "=================================================="
    echo "  Email Security Breach Checker v2.0 - Setup"
    echo "=================================================="
    echo ""
    
    cd "$(dirname "$0")"
    
    check_python_version
    check_essential_files
    setup_virtual_environment
    install_dependencies
    setup_configuration
    setup_directories
    start_program
}

set -e
main "$@"