import { NextRequest, NextResponse } from 'next/server';

const DISCORD_WEBHOOK_URL = process.env.DISCORD_WEBHOOK_URL;

export async function POST(request: NextRequest) {
  try {
    const { content, embeds, channel } = await request.json();
    
    if (!DISCORD_WEBHOOK_URL) {
      return NextResponse.json(
        { error: 'Discord webhook not configured' },
        { status: 500 }
      );
    }

    // Send to Discord webhook
    const response = await fetch(DISCORD_WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content,
        embeds,
        username: 'AirCle X Monitor',
        avatar_url: 'https://pbs.twimg.com/profile_images/1729618006259572736/Hb8dpjJt_400x400.jpg',
      }),
    });

    if (!response.ok) {
      throw new Error(`Discord API error: ${response.status}`);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Discord webhook error:', error);
    return NextResponse.json(
      { error: 'Failed to send Discord message' },
      { status: 500 }
    );
  }
}

// Send monitoring alert with action buttons
export async function PUT(request: NextRequest) {
  try {
    const { 
      account, 
      originalUrl, 
      translatedText, 
      generatedDraft,
      buzzTemplate,
      mediaUrls,
      isVideo
    } = await request.json();

    if (!DISCORD_WEBHOOK_URL) {
      return NextResponse.json(
        { error: 'Discord webhook not configured' },
        { status: 500 }
      );
    }

    // Create Discord embed
    const embed = {
      title: `🔔 ${account} の新規投稿`,
      description: translatedText.substring(0, 4096),
      color: 0x1d9bf0,
      fields: [
        {
          name: '型',
          value: buzzTemplate,
          inline: true,
        },
        {
          name: '動画',
          value: isVideo ? '✅ はい' : '❌ いいえ',
          inline: true,
        },
        {
          name: '生成ドラフト',
          value: '```\n' + generatedDraft.substring(0, 1000) + '\n```',
        },
      ],
      timestamp: new Date().toISOString(),
      footer: {
        text: 'AirCle X Monitor',
      },
    };

    // Send with action row
    const response = await fetch(DISCORD_WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: `📢 **${account}** が投稿しました！\n元URL: ${originalUrl}\n\nこれ投稿しとこうか？ 👇`,
        embeds: [embed],
        components: [
          {
            type: 1,
            components: [
              {
                type: 2,
                label: '✅ 投稿する',
                style: 3,
                custom_id: `post_${account}_${Date.now()}`,
              },
              {
                type: 2,
                label: '❌ スキップ',
                style: 4,
                custom_id: `skip_${account}_${Date.now()}`,
              },
              {
                type: 2,
                label: '📋 コピー',
                style: 2,
                custom_id: `copy_${account}_${Date.now()}`,
              },
            ],
          },
        ],
        username: 'AirCle X Monitor',
        avatar_url: 'https://pbs.twimg.com/profile_images/1729618006259572736/Hb8dpjJt_400x400.jpg',
      }),
    });

    if (!response.ok) {
      throw new Error(`Discord API error: ${response.status}`);
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Discord alert error:', error);
    return NextResponse.json(
      { error: 'Failed to send Discord alert' },
      { status: 500 }
    );
  }
}
