import { findings } from "../../components/findings-data";

export async function GET() {
  return Response.json({ items: findings, next_cursor: null });
}
