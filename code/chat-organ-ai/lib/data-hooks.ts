"use client";

import { useMemo } from "react";
import { getWorkspaceSnapshot } from "./mock-data";
import type { TaskStatus, Message, Task } from "./types/workspace";

export function useWorkspaceSnapshot() {
  return useMemo(() => getWorkspaceSnapshot(), []);
}

export function useMessages(): Message[] {
  const snapshot = useWorkspaceSnapshot();
  return snapshot.messages;
}

export function useTasksByStatus(status: TaskStatus): Task[] {
  const snapshot = useWorkspaceSnapshot();
  return useMemo(
    () => snapshot.tasks.filter((task) => task.status === status),
    [snapshot, status]
  );
}
