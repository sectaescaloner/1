const { Client } = require('discord.js-selfbot-v13');
const { setTimeout } = require('timers/promises');

// --- CONFIGURACIÓN DINÁMICA ---
const token = process.argv[2]; 
const startCommand = process.argv[3];
const messageToSend = process.argv[4];
const amount = 999999; // Infinito hasta que el runner muera

// Delays ajustados para NO quemar la cuenta
const MIN_DELAY = 4; // 4 segundos minimo
const MAX_DELAY = 7; // 7 segundos maximo
const RECOVERY_DELAY = 45; // 45 segundos si hay rate limit

let currentDelay = MAX_DELAY;
const client = new Client({ checkUpdate: false });

function getRandomDelay(min, max) {
    return Math.round((Math.random() * (max - min) + min) * 1000);
}

client.on('ready', () => {
    console.log(`✅ Hydra-Selfbot Online: ${client.user.tag}`);
    console.log(`> Esperando comando: ${startCommand}`);
});

client.on('messageCreate', async (message) => {
    if (message.author.id !== client.user.id) return;
    if (message.content.startsWith(startCommand)) {
        const targetChannel = message.channel;
        console.log(`🚀 Iniciando en: ${targetChannel.name || 'MD'}`);
        
        let messageNumber = 0;
        while (messageNumber < amount) {
            try {
                await setTimeout(getRandomDelay(MIN_DELAY, currentDelay));
                await targetChannel.send(messageToSend);
                messageNumber++;
                currentDelay = MIN_DELAY;
                console.log(`[OK] Petición #${messageNumber} enviada.`);
            } catch (error) {
                if (error.code === 429) {
                    console.error(`⚠️ RATE LIMIT: Esperando ${RECOVERY_DELAY}s...`);
                    await setTimeout(RECOVERY_DELAY * 1000);
                    continue;
                } else if (error.code === 50001) {
                    console.error(`🚫 Sin permisos en este canal.`);
                    return;
                }
                console.error(`Error: ${error.message}`);
                await setTimeout(5000);
            }
        }
    }
});

client.login(token);
