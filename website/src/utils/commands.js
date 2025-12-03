export const THEMES = [
    'default', 'matrix', 'kth', 'dark', 'retro', 'cyberpunk', 'dracula',
    'monokai', 'solarized-light', 'solarized-dark', 'nord', 'synthwave',
    'ubuntu', 'red-alert', 'blue-screen', 'sakura', 'soft-sakura', 'chroma', 'purple'
];

export const COMMANDS = {
    help: {
        description: 'Show list of supported commands',
        execute: () => ({
            type: 'response',
            text: `Available commands:
  help      - Show this help message
  about     - Learn more about KTH-GPT
  contact   - Get contact information
  copy      - Copy the last AI response to clipboard
  theme     - Change terminal theme (usage: theme <name>)
  clear     - Clear the terminal
  
  ...and some hidden ones to discover!`
        })
    },
    about: {
        description: 'Info about the website / project',
        execute: () => ({
            type: 'response',
            text: 'KTH-GPT is a RAG-powered AI assistant designed by students for students. It helps you find accurate answers from course materials and university documents.'
        })
    },
    contact: {
        description: 'Show contact info',
        execute: () => ({
            type: 'response',
            text: 'GitHub: https://github.com/alnordg/KTH-GPT\nCreated by: Alno & Guma',
            html: true,
            link: 'https://github.com/alnordg/KTH-GPT'
        })
    },
    sudo: {
        description: '???',
        execute: () => ({ type: 'response', text: 'Nice try. Permission denied.' })
    },
    kth: {
        description: 'Fun facts about KTH',
        execute: () => {
            const facts = [
                "KTH was founded in 1827.",
                "KTH stands for Kungliga Tekniska Högskolan.",
                "The KTH motto is 'Vetenskap och Konst' (Science and Art).",
                "There is a nuclear reactor (R1) under the KTH campus (decommissioned).",
                "KTH is Sweden's largest technical university."
            ];
            return { type: 'response', text: facts[Math.floor(Math.random() * facts.length)] };
        }
    },
    ls: {
        description: 'List files',
        execute: () => ({
            type: 'response',
            text: `drwxr-xr-x  user  staff   128 Dec 2 13:37 .
drwxr-xr-x  root  root    256 Dec 1 10:00 ..
-rw-r--r--  user  staff  1337 Dec 2 12:00 logo.txt
-rw-r--r--  user  staff   420 Dec 2 12:00 secrets.env
drwxr-xr-x  user  staff   512 Dec 2 12:00 node_modules (black hole)`
        })
    },
    cat: {
        description: 'Read file',
        allowArgs: true,
        execute: (args) => {
            if (args[0] === 'logo.txt') {
                return {
                    type: 'response',
                    text: `
██╗  ██╗████████╗██╗  ██╗         ██████╗ ██████╗ ████████╗
██║ ██╔╝╚══██╔══╝██║  ██║        ██╔════╝ ██╔══██╗╚══██╔══╝
█████╔╝    ██║   ███████║ █████╗ ██║  ███╗██████╔╝   ██║   
██╔═██╗    ██║   ██╔══██║ ╚════╝ ██║   ██║██╔═══╝    ██║   
██║  ██╗   ██║   ██║  ██║        ╚██████╔╝██║        ██║   
╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝         ╚═════╝ ╚═╝        ╚═╝     
            `
                };
            }
            return { type: 'response', text: `cat: ${args[0] || ''}: No such file or directory` };
        }
    },
    clear: {
        description: 'Clear terminal',
        execute: () => ({ type: 'clear' })
    },
    theme: {
        description: 'Change theme',
        allowArgs: true,
        execute: (args) => {
            if (!args[0]) return { type: 'response', text: `Usage: theme <name>\nAvailable themes: ${THEMES.join(', ')}` };
            if (THEMES.includes(args[0].toLowerCase())) {
                return { type: 'theme', theme: args[0].toLowerCase() };
            }
            return { type: 'response', text: `Theme '${args[0]}' not found. Available: ${THEMES.join(', ')}` };
        }
    },
    matrix: {
        description: 'Enter the matrix',
        execute: () => ({ type: 'theme', theme: 'matrix' })
    },
    brainrot: {
        description: '???',
        execute: () => ({ type: 'brainrot' })
    },
    copy: {
        description: 'Copy the last AI response to clipboard',
        execute: () => ({ type: 'copy' })
    }
};

export const processCommand = (input) => {
    const parts = input.trim().split(/\s+/);
    const command = parts[0].toLowerCase();
    const args = parts.slice(1);

    if (COMMANDS[command]) {
        const cmdDef = COMMANDS[command];
        // If command doesn't allow args but args were provided, treat as normal text
        if (!cmdDef.allowArgs && args.length > 0) {
            return null;
        }
        return cmdDef.execute(args);
    }
    return null;
};
