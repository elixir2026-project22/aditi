import { useEffect, useState } from "react";

import { pathwayApi } from "../../modules/pathways/services";

export type BackendStatus =
  | "connecting"
  | "online"
  | "offline";

export interface BackendStatusState {
  status: BackendStatus;
  availableLayouts: string[];
  error: string | null;
}

const INITIAL_STATE: BackendStatusState = {
  status: "connecting",
  availableLayouts: [],
  error: null,
};

export function useBackendStatus(): BackendStatusState {
  const [state, setState] =
    useState<BackendStatusState>(INITIAL_STATE);

  useEffect(() => {
    let active = true;

    async function checkBackend(): Promise<void> {
      try {
        const health = await pathwayApi.checkHealth();

        if (
          health.application !== "Aditi" ||
          health.status !== "ok"
        ) {
          throw new Error(
            "The backend returned an unexpected health response.",
          );
        }

        if (!active) {
          return;
        }

        setState({
          status: "online",
          availableLayouts: [],
          error: null,
        });

        try {
          const layouts = await pathwayApi.getAvailableLayouts();

          if (!active) {
            return;
          }

          setState({
            status: "online",
            availableLayouts: layouts,
            error: null,
          });
        } catch (error) {
          if (!active) {
            return;
          }

          setState((previous) => ({
            ...previous,
            error:
              error instanceof Error
                ? error.message
                : "Unable to retrieve pathway layouts.",
          }));
        }
      } catch (error) {
        if (!active) {
          return;
        }

        setState({
          status: "offline",
          availableLayouts: [],
          error:
            error instanceof Error
              ? error.message
              : "Unable to connect to the Aditi backend.",
        });
      }
    }

    void checkBackend();

    return () => {
      active = false;
    };
  }, []);

  return state;
}