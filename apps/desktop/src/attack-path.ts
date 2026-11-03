import type { GraphState } from "./graph-model";
import type { AttackPathResponse, AttackPathResult } from "./graph-types";
import { reviewStatePresentation, type ReviewStatePresentation } from "./review-status";

export interface AttackPathOption {
  id: string;
  label: string;
  sourceFile: string;
  goalId: string;
  result: AttackPathResult;
}

export interface AttackPathPresentation {
  stepNodeIds: string[];
  pathEdgeIds: string[];
  dimmedNodeIds: string[];
  dimmedEdgeIds: string[];
}

/** Converts one unmodified PR #132 goal response into selector options. */
export function attackPathOptions(response: AttackPathResponse): AttackPathOption[] {
  return response.paths.map((path, index) => ({
    id: `${response.goal}:${path.authored_path ?? "computed"}:alternative-${index + 1}`,
    label: attackPathOptionLabel(response, path, index),
    sourceFile: response.file,
    goalId: response.goal,
    result: {
      steps: [...path.steps],
      goal_step: path.goal_step,
      ...(path.authored_path ? { authored_path: path.authored_path } : {}),
      review: { ...path.review },
    },
  }));
}

function attackPathOptionLabel(
  response: AttackPathResponse,
  path: AttackPathResult,
  index: number,
): string {
  const goal = titleCaseIdentifier(shortId(response.goal));
  const status = attackPathReviewState(path.review);
  if (response.paths.length > 1) {
    return `${goal} — Alternative ${index + 1} (${status.label})`;
  }
  // "Reviewed" is reserved for an accepted path. The engine's `reviewed` flag
  // follows the Assertion alone, so a negative Review must not inherit it.
  return status.kind === "accepted"
    ? `${goal} — Reviewed (${status.label})`
    : `${goal} — ${status.label}`;
}

export function attackPathOptionsForResponses(
  responses: readonly AttackPathResponse[],
): AttackPathOption[] {
  return responses.flatMap(attackPathOptions);
}

export function attackPathPresentation(
  state: GraphState,
  path?: AttackPathResult,
): AttackPathPresentation {
  if (!path) return { stepNodeIds: [], pathEdgeIds: [], dimmedNodeIds: [], dimmedEdgeIds: [] };

  const loadedNodeIds = new Set(state.nodes.map((node) => node.id));
  const stepNodeIds = path.steps.filter((id) => loadedNodeIds.has(id));
  // PR #132 returns a topologically ordered set of steps. An AND path can have
  // two branches whose steps are interleaved in that ordering, so adjacency in
  // the array does not imply adjacency in the graph. Highlight every authored
  // directed `precedes` edge whose two endpoints belong to this alternative.
  const pathStepIds = new Set(path.steps);
  const pathEdgeIds = state.edges
    .filter((edge) => (
      edge.relationshipType === "precedes"
      && pathStepIds.has(edge.source)
      && pathStepIds.has(edge.target)
    ))
    .map((edge) => edge.id);

  const highlightedNodes = new Set(stepNodeIds);
  const highlightedEdges = new Set(pathEdgeIds);
  return {
    stepNodeIds,
    pathEdgeIds,
    dimmedNodeIds: state.nodes.filter((node) => !highlightedNodes.has(node.id)).map((node) => node.id),
    dimmedEdgeIds: state.edges.filter((edge) => !highlightedEdges.has(edge.id)).map((edge) => edge.id),
  };
}

/** The shared review presentation for one path's PR #132 `review` record. */
export function attackPathReviewState(review: AttackPathResult["review"]): ReviewStatePresentation {
  return reviewStatePresentation(review.assertion_status, review.review_status);
}

export function attackPathReviewLabel(review: AttackPathResult["review"]): string {
  const parts = [attackPathReviewState(review).description];
  if (review.assertion_status) parts.push(`assertion: ${humanizeStatus(review.assertion_status)}`);
  if (review.review_status) parts.push(`review: ${humanizeStatus(review.review_status)}`);
  return parts.join(" · ");
}

function shortId(id: string): string {
  return id.includes(":") ? id.slice(id.indexOf(":") + 1) : id;
}

function humanizeStatus(status: string): string {
  return status.replace(/_/g, " ");
}

function titleCaseIdentifier(value: string): string {
  return value
    .split(/[-_]/)
    .map((part) => {
      const upper = part.toUpperCase();
      if (upper === "IMDS" || upper === "XXE") return upper;
      return `${part.charAt(0).toUpperCase()}${part.slice(1)}`;
    })
    .join(" ");
}
