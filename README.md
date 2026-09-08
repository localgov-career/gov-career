# 地方公務員キャリア

地方公務員から民間企業への転職に特化した情報メディアのMVP。

## 開発

```bash
npm install
npm run dev
```

## ビルド

```bash
npm run build
```

## Cloudflare

静的AstroサイトとしてCloudflare Pages / Workers Assetsへデプロイできます。
本番ドメインは `src/data/site.js` の `siteUrl` を変更してください。
canonical・OGP・サイトマップ・robots.txtで同じ設定を使用します。
サイトマップとrobots.txtはビルド完了時に生成されるため、確認には開発サーバーではなくビルド後のプレビューを使ってください。

## 検証

```bash
npm run build
python3 scripts/check-site.py
npm run preview
```

HTMLの見出し、固有の説明文、canonical、内部リンクとページ内リンク、サイトマップとの一致を確認します。
テンプレートは公開ルートにならない `src/templates/` に置きます。
`BaseLayout` の `updatedDate` は内容を確認・更新したページだけに設定し、執筆者情報や確認日を推測で補わないでください。

## 次の実装

- Search Console / Analytics
- CTAクリック計測
- 運営者の公開プロフィール・問い合わせ先（本人確認が必要）
- 未改訂記事の内容確認・具体例の補充
