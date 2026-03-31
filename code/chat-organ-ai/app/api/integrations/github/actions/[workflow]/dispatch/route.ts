import { NextResponse } from "next/server";

type Params = {
  params: {
    workflow: string;
  };
};

export async function POST(request: Request, { params }: Params) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    return NextResponse.json(
      {
        error:
          "GitHub Actions を実行するには .env.local (サーバ側) に GITHUB_TOKEN を設定してください。",
        instruction:
          "GitHub Settings > Developer settings > Personal access tokens から必要最小権限 (workflow) で発行し、.env.local に GITHUB_TOKEN=<token> を記入します。",
      },
      { status: 400 }
    );
  }

  const body = await request.json();
  const runId = Date.now();

  return NextResponse.json({
    workflow: params.workflow,
    repository: body.repository ?? "unknown/repo",
    ref: body.ref ?? "main",
    status: "queued",
    runId,
    note:
      "サンドボックスでは実際の GitHub API には到達しません。GITHUB_TOKEN 設定後に Temporal/DevOps Agent から実行してください。",
  });
}
