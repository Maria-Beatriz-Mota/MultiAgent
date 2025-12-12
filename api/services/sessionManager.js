/**
 * Gerenciador de Sessões para Follow-ups
 * Mantém contexto de conversas entre requisições
 */

// Armazenamento em memória (sessões expiram após 30 minutos de inatividade)
const sessions = new Map();
const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutos

/**
 * Cria nova sessão ou recupera existente
 * @param {string} sessionId - ID da sessão (opcional)
 * @returns {object} - Objeto da sessão
 */
function getOrCreateSession(sessionId) {
    if (sessionId && sessions.has(sessionId)) {
        const session = sessions.get(sessionId);
        
        // Verificar se expirou
        if (Date.now() - session.lastActivity > SESSION_TIMEOUT) {
            console.log('[SESSION] Sessão expirada:', sessionId);
            sessions.delete(sessionId);
            return createNewSession();
        }
        
        // Atualizar timestamp
        session.lastActivity = Date.now();
        console.log('[SESSION] Sessão recuperada:', sessionId, `(${session.chatHistory.length} mensagens)`);
        return session;
    }
    
    return createNewSession();
}

/**
 * Cria nova sessão
 * @returns {object} - Nova sessão
 */
function createNewSession() {
    const sessionId = generateSessionId();
    const session = {
        id: sessionId,
        chatHistory: [],
        clinicalData: null,
        lastResult: null,
        createdAt: Date.now(),
        lastActivity: Date.now()
    };
    
    sessions.set(sessionId, session);
    console.log('[SESSION] Nova sessão criada:', sessionId);
    return session;
}

/**
 * Atualiza sessão com novos dados
 * @param {string} sessionId - ID da sessão
 * @param {object} updates - Dados para atualizar
 */
function updateSession(sessionId, updates) {
    if (!sessions.has(sessionId)) {
        console.warn('[SESSION] Tentou atualizar sessão inexistente:', sessionId);
        return;
    }
    
    const session = sessions.get(sessionId);
    Object.assign(session, updates);
    session.lastActivity = Date.now();
    
    console.log('[SESSION] Sessão atualizada:', sessionId);
}

/**
 * Adiciona mensagem ao histórico
 * @param {string} sessionId - ID da sessão
 * @param {string} role - 'user' ou 'assistant'
 * @param {string} content - Conteúdo da mensagem
 */
function addMessage(sessionId, role, content) {
    if (!sessions.has(sessionId)) {
        console.warn('[SESSION] Sessão não existe:', sessionId);
        return;
    }
    
    const session = sessions.get(sessionId);
    session.chatHistory.push({ role, content });
    session.lastActivity = Date.now();
    
    // Limitar histórico a 20 mensagens (10 trocas)
    if (session.chatHistory.length > 20) {
        session.chatHistory = session.chatHistory.slice(-20);
    }
}

/**
 * Limpa sessão
 * @param {string} sessionId - ID da sessão
 */
function clearSession(sessionId) {
    if (sessions.delete(sessionId)) {
        console.log('[SESSION] Sessão removida:', sessionId);
        return true;
    }
    return false;
}

/**
 * Gera ID único para sessão
 * @returns {string} - ID da sessão
 */
function generateSessionId() {
    return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Limpa sessões expiradas (executar periodicamente)
 */
function cleanupExpiredSessions() {
    const now = Date.now();
    let cleaned = 0;
    
    for (const [sessionId, session] of sessions.entries()) {
        if (now - session.lastActivity > SESSION_TIMEOUT) {
            sessions.delete(sessionId);
            cleaned++;
        }
    }
    
    if (cleaned > 0) {
        console.log(`[SESSION] ${cleaned} sessões expiradas removidas`);
    }
}

// Executar limpeza a cada 5 minutos
setInterval(cleanupExpiredSessions, 5 * 60 * 1000);

module.exports = {
    getOrCreateSession,
    updateSession,
    addMessage,
    clearSession,
    generateSessionId
};
