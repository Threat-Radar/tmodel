// The engine's read-only GET /proposals payload (engine/engine/core.py, DL-0046).
// The app never writes proposals or decisions: an agent proposes with `tmodel
// propose`, and only the sponsor decides, with `tmodel accept` in a pull request.
import type { SdlProposal } from "./sdl-types";

export type ProposalSummary = SdlProposal;

/** A saved KG view the Graph tab can load: the model's own, or a proposed one. */
export interface SavedView {
  id: string;
  name: string;
  description: string;
  focus_query: string;
  /** `accepted` (in the model), `proposed` (a pending proposal adds or edits it),
   *  or `proposed_removal` (a pending proposal would remove it). */
  state: "accepted" | "proposed" | "proposed_removal";
  proposal: string | null;
  node_ids: string[];
  error?: string;
}

export interface ProposalsResponse {
  file: string;
  kind: "threat" | "sdl";
  proposals: ProposalSummary[];
  views: SavedView[];
}

export interface ProposalsDataProvider {
  getProposals(file: string, signal?: AbortSignal): Promise<ProposalsResponse>;
}
