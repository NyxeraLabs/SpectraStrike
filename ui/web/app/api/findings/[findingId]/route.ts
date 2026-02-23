import { findings } from "../../../components/findings-data";

export async function GET(
  _request: Request,
  context: { params: Promise<{ findingId: string }> }
) {
  const params = await context.params;
  const finding = findings.find((item) => item.finding_id === params.findingId);
  if (!finding) {
    return Response.json({ error: "not_found" }, { status: 404 });
  }
  return Response.json(finding);
}
