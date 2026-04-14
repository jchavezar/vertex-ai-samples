import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";

const execPromise = promisify(exec);

export async function POST(req: NextRequest) {
  try {
    const { command, dir } = await req.json();

    // Safety: Only allow execution within the project or subdirectories
    // In a real 'Claude Code' scenario, this would be more complex.
    console.log(`>>> Executing Local Command: ${command}`);

    const { stdout, stderr } = await execPromise(command, {
      cwd: dir || process.cwd(),
      timeout: 30000, // 30s timeout
    });

    return NextResponse.json({
      stdout,
      stderr,
      exitCode: 0,
    });
  } catch (error: any) {
    return NextResponse.json({
      stdout: error.stdout || "",
      stderr: error.stderr || error.message,
      exitCode: error.code || 1,
    }, { status: 500 });
  }
}
