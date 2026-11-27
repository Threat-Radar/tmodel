// #290: the one place the app asks the desktop host for something it cannot do
// itself. #288's routes that take a folder or file path refuse any request with
// an Origin header, so the webview can never call them: the host shows a native
// picker, calls the route, and hands back only the model id the engine answered
// with (engine/MODEL_WORKSPACE.md). The host also owns the session token the
// /workspace/* and /reviews/* routes need, and keeps it in memory.
//
// The Tauri host does not implement these commands yet. Until it does, the
// probe below finds no session and projects stay unavailable, so the app is as
// read-only as before. What the host must add is listed in design-log/0077.

/** One host step: a native picker, then #288's host-only route. */
export type HostProjectStep =
  /** Choose a project folder: POST /workspace/host/open-project {path}. */
  | { kind: "open-project" }
  /** Choose a saved threat model YAML file: POST /workspace/host/open-file {path}, read-only. */
  | { kind: "open-file" }
  /** Choose a new project folder: POST /workspace/host/create-project {path, source_file | model_id, name?}. */
  | { kind: "create-project"; from: ProjectStart };

/**
 * What a new project starts from. An imported model's text has no file yet: the
 * host writes it to a file, opens that with open-file, and starts the project
 * from the file's model id.
 */
export type ProjectStart =
  | { source_file: string }
  | { model_id: string }
  | { model_text: string; name: string };

export interface ProjectHost {
  /** The host's session token, or undefined when this host offers none. */
  session(): string | undefined;
  /** The model id the engine answered with, or null when the user cancelled the picker. */
  hostProjectStep(step: HostProjectStep): Promise<string | null>;
}

export const NO_HOST_REASON = "Projects need the desktop app to choose folders and files, which this build cannot do yet.";

export const NO_PROJECT_HOST: ProjectHost = {
  session: () => undefined,
  hostProjectStep: () => Promise.reject(new Error(NO_HOST_REASON)),
};

/** Tauri commands the host is to provide; their names are this module's contract with it. */
export const HOST_SESSION_COMMAND = "project_host_session";
export const HOST_STEP_COMMAND = "project_host_step";

/**
 * Asks the Tauri host for its session. A host without the commands, or outside
 * Tauri (a browser on the Vite server), gives NO_PROJECT_HOST.
 */
export async function connectProjectHost(): Promise<ProjectHost> {
  const { invoke, isTauri } = await import("@tauri-apps/api/core");
  if (!isTauri()) return NO_PROJECT_HOST;
  let token: unknown;
  try {
    token = await invoke(HOST_SESSION_COMMAND);
  } catch {
    return NO_PROJECT_HOST;
  }
  if (typeof token !== "string" || token.length < 32) return NO_PROJECT_HOST;
  return {
    session: () => token as string,
    hostProjectStep: async (step) => {
      const answer = await invoke(HOST_STEP_COMMAND, { step });
      if (answer === null) return null;
      if (typeof answer !== "string" || !/^(project|file):[0-9a-f]{32}$/.test(answer)) {
        throw new Error("The desktop host returned no model id.");
      }
      return answer;
    },
  };
}

/** A host that can change once the probe answers; every caller reads it at the time of use. */
export class ProjectHostHolder implements ProjectHost {
  private host: ProjectHost = NO_PROJECT_HOST;

  set(host: ProjectHost): void {
    this.host = host;
  }

  session(): string | undefined {
    return this.host.session();
  }

  hostProjectStep(step: HostProjectStep): Promise<string | null> {
    return this.host.hostProjectStep(step);
  }
}
