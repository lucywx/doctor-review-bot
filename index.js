const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const path = require('path');
const dotenv = require('dotenv');
const DoctorSearchBot = require('./src/bot/DoctorSearchBot');
const SearchAggregator = require('./src/search/SearchAggregator');

// 加载环境变量
dotenv.config();

class WhatsAppDoctorBot {
    constructor() {
        this.client = new Client({
            authStrategy: new LocalAuth({
                clientId: "doctor-search-bot"
            }),
            puppeteer: {
                headless: true,
                args: ['--no-sandbox', '--disable-setuid-sandbox']
            }
        });
        
        this.searchBot = new DoctorSearchBot();
        this.searchAggregator = new SearchAggregator();
        this.setupEventHandlers();
    }

    setupEventHandlers() {
        // 二维码生成
        this.client.on('qr', (qr) => {
            console.log('🔗 请扫描二维码登录WhatsApp:');
            qrcode.generate(qr, { small: true });
        });

        // 登录成功
        this.client.on('ready', () => {
            console.log('✅ WhatsApp Bot已准备就绪！');
            console.log('🤖 医生评价搜索机器人已启动');
        });

        // 消息处理
        this.client.on('message', async (message) => {
            try {
                await this.handleMessage(message);
            } catch (error) {
                console.error('处理消息时出错:', error);
                await message.reply('❌ 处理您的请求时出现错误，请稍后重试。');
            }
        });

        // 错误处理
        this.client.on('auth_failure', (msg) => {
            console.error('认证失败:', msg);
        });

        this.client.on('disconnected', (reason) => {
            console.log('连接断开:', reason);
        });
    }

    async handleMessage(message) {
        const messageText = message.body.toLowerCase().trim();
        
        // 忽略机器人自己的消息
        if (message.fromMe) return;

        // 帮助命令
        if (messageText === '帮助' || messageText === 'help' || messageText === '/help') {
            await this.sendHelpMessage(message);
            return;
        }

        // 开始搜索命令
        if (messageText.startsWith('搜索医生') || messageText.startsWith('search doctor')) {
            const doctorName = messageText.replace(/^(搜索医生|search doctor)\s*/i, '').trim();
            if (doctorName) {
                await this.searchDoctorReviews(message, doctorName);
            } else {
                await message.reply('请提供医生姓名，例如：搜索医生 张医生');
            }
            return;
        }

        // 默认回复
        if (messageText.length > 0) {
            await message.reply(
                '👋 欢迎使用医生评价搜索机器人！\n\n' +
                '📋 可用命令：\n' +
                '• 搜索医生 [医生姓名] - 搜索医生评价\n' +
                '• 帮助 - 显示帮助信息\n\n' +
                '💡 示例：搜索医生 李医生'
            );
        }
    }

    async searchDoctorReviews(message, doctorName) {
        try {
            // 发送搜索开始消息
            await message.reply(`🔍 正在搜索 "${doctorName}" 的评价信息，请稍候...`);

            // 执行多源搜索
            const searchResults = await this.searchAggregator.searchDoctorReviews(doctorName);
            
            if (searchResults && searchResults.length > 0) {
                // 格式化并发送结果
                const formattedResults = this.formatSearchResults(searchResults, doctorName);
                await message.reply(formattedResults);
            } else {
                await message.reply(`❌ 未找到关于 "${doctorName}" 的评价信息。请尝试使用不同的搜索词。`);
            }
        } catch (error) {
            console.error('搜索医生评价时出错:', error);
            await message.reply('❌ 搜索过程中出现错误，请稍后重试。');
        }
    }

    formatSearchResults(results, doctorName) {
        let response = `📊 关于 "${doctorName}" 的评价汇总：\n\n`;
        
        results.forEach((result, index) => {
            response += `📍 ${result.source}:\n`;
            response += `⭐ 评分: ${result.rating || 'N/A'}\n`;
            response += `💬 评价: ${result.review || '暂无评价'}\n`;
            response += `🔗 链接: ${result.url || 'N/A'}\n`;
            if (result.location) {
                response += `📍 位置: ${result.location}\n`;
            }
            response += `\n`;
        });

        response += `📈 搜索完成！共找到 ${results.length} 条评价信息。`;
        return response;
    }

    async sendHelpMessage(message) {
        const helpText = 
            '🤖 医生评价搜索机器人帮助\n\n' +
            '📋 可用命令：\n' +
            '• 搜索医生 [医生姓名] - 搜索指定医生的评价\n' +
            '• 帮助 - 显示此帮助信息\n\n' +
            '💡 使用示例：\n' +
            '• 搜索医生 张医生\n' +
            '• 搜索医生 李主任\n' +
            '• 搜索医生 王教授\n\n' +
            '🔍 搜索范围包括：\n' +
            '• Google Maps 评价\n' +
            '• Facebook 评价\n' +
            '• 医疗论坛评价\n' +
            '• 其他在线评价平台\n\n' +
            '⚡ 机器人会自动聚合多源评价信息，为您提供全面的医生评价汇总。';
        
        await message.reply(helpText);
    }

    async start() {
        try {
            await this.client.initialize();
            console.log('🚀 WhatsApp Doctor Search Bot 启动中...');
        } catch (error) {
            console.error('启动机器人时出错:', error);
        }
    }
}

// 启动机器人
const bot = new WhatsAppDoctorBot();
bot.start();

// 优雅关闭
process.on('SIGINT', async () => {
    console.log('\n🛑 正在关闭机器人...');
    await bot.client.destroy();
    process.exit(0);
});

module.exports = WhatsAppDoctorBot;
