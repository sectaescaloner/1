const { Client } = require('discord.js-selfbot-v13');
const { setTimeout } = require('timers/promises');

// Captura de argumentos del YAML
const token = process.argv[2]; 
const startCommand = process.argv[3];
const messageToSend = process.argv[4];

// --- CONFIGURACION HUMANA ---
const TU_ID = "1228540602497630310"; // CAMBIA ESTO POR TU ID DE DISCORD
const MIN_DELAY = 7;  // 5 segundos
const MAX_DELAY = 10; // 10 segundos
const COOLDOWN_429 = 100; // 1 minuto si hay Rate Limit

const client = new Client({ checkUpdate: false });

client.on('ready', () => {
    console.log(`✅ Conectado como: ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
    // Solo responder a tu cuenta
    if (message.author.id !== TU_ID) return;

    if (message.content.startsWith(startCommand)) {
        const channel = message.channel;
        console.log(`🚀 Activando en: ${channel.id}`);

        // Borrar el comando de activacion para limpiar el rastro
        try {
            await message.delete();
        } catch (e) {
            console.log("No pude borrar el comando, ignorando...");
        }

        // Bucle de envío respetuoso
        while (true) {
            try {
                // Delay aleatorio para parecer humano
                const delay = Math.floor(Math.random() * (MAX_DELAY - MIN_DELAY + 1)) + MIN_DELAY;
                await setTimeout(delay);

                await channel.send(messageToSend);
                console.log(`[SENT] Mensaje enviado. Proximo en ${delay/1000}s`);

            } catch (error) {
                if (error.code === 429) {
                    console.log(`⚠️ Rate limit detectado. Pausando ${COOLDOWN_429/1000}s para ser buenos con Discord.`);
                    await setTimeout(COOLDOWN_429);
                } else {
                    console.error("Error inesperado:", error.message);
                    await setTimeout(5000);
                }
            }
        }
    }
});

client.login(token).catch(err => {
    console.error("No se pudo iniciar sesion. Revisa el Token.");
    process.exit(1);
});
