#!/bin/bash

# Colori per l'output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

LOG_DIR="logs"
mkdir -p $LOG_DIR

function start() {
    echo -e "${GREEN}Avvio del sistema Nexus CRM...${NC}"

    # 1. Avvio Backend
    if [ -d "backend/venv" ]; then
        source backend/venv/bin/activate
    else
        echo -e "${RED}Virtual environment non trovato in backend/venv!${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Avvio Backend (Django) su port 8000...${NC}"
    # Usa python -u per forzare l'output non bufferizzato (fix log vuoti)
    nohup python -u backend/manage.py runserver > $LOG_DIR/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > $LOG_DIR/backend.pid

    # 2. Avvio Frontend
    echo -e "${YELLOW}Avvio Frontend (Vite) su port 5173...${NC}"
    cd frontend
    # Usa npm run dev con output rediretto
    nohup npm run dev > ../$LOG_DIR/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    echo $FRONTEND_PID > $LOG_DIR/frontend.pid

    echo -e "${GREEN}Tutto avviato!${NC}"
    echo -e "Frontend: http://localhost:5173"
    echo -e "Backend:  http://localhost:8000"
    echo -e "Usa './manage.sh logs backend' o './manage.sh logs frontend' per i log."
}

function stop() {
    echo -e "${RED}Arresto dei servizi...${NC}"
    pkill -f "manage.py runserver"
    pkill -f "vite"
    rm -f $LOG_DIR/*.pid
    echo -e "${GREEN}Servizi fermati.${NC}"
}

function status() {
    if pgrep -f "manage.py runserver" > /dev/null; then
        echo -e "${GREEN}Backend: ONLINE${NC}"
    else
        echo -e "${RED}Backend: OFFLINE (Controlla logs/backend.log)${NC}"
    fi

    if pgrep -f "vite" > /dev/null; then
        echo -e "${GREEN}Frontend: ONLINE${NC}"
    else
        echo -e "${RED}Frontend: OFFLINE${NC}"
    fi
}

function logs() {
    TARGET=${1:-backend} # Default a backend se vuoto

    if [ "$TARGET" == "frontend" ]; then
        echo -e "${YELLOW}Log Frontend (Vite) - CTRL+C per uscire...${NC}"
        if [ -f "$LOG_DIR/frontend.log" ]; then
            tail -f $LOG_DIR/frontend.log
        else
            echo -e "${RED}File log non trovato: $LOG_DIR/frontend.log${NC}"
        fi
    elif [ "$TARGET" == "backend" ]; then
        echo -e "${YELLOW}Log Backend (Django) - CTRL+C per uscire...${NC}"
        if [ -f "$LOG_DIR/backend.log" ]; then
            tail -f $LOG_DIR/backend.log
        else
            echo -e "${RED}File log non trovato: $LOG_DIR/backend.log${NC}"
        fi
    else
        echo -e "${RED}Target non valido: $TARGET${NC}"
        echo "Uso: ./manage.sh logs [backend|frontend]"
    fi
}

case "$1" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 2; start ;;
    status) status ;;
    logs) logs "$2" ;;
    *) echo "Usa: ./manage.sh {start|stop|restart|status|logs [backend|frontend]}" ;;
esac
