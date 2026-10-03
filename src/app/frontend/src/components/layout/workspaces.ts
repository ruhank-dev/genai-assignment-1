export interface Workspace {
  to: string;
  name: string; // full workspace name (assignment wording)
  tab: string; // bottom tab text (Stitch)
  hint: string;
  icon: string; // Material Symbols icon name
}

export const WORKSPACES: Workspace[] = [
  { to: "/universal", name: "Universal Restoration", tab: "Universal Restoration", hint: "Task 1 · one autoencoder", icon: "auto_fix_high" },
  { to: "/hard-routed", name: "Hard-Routed Restoration", tab: "Hard-Routed", hint: "Task 2 · classifier + specialists", icon: "alt_route" },
  { to: "/soft-moe", name: "Soft Mixture-of-Experts Restoration", tab: "Mixture of Experts", hint: "Task 3 · gated blend", icon: "layers" },
  { to: "/face-to-sketch", name: "Face-to-Sketch Generator", tab: "Face-to-Sketch", hint: "Task 4 · conditional GAN", icon: "draw" },
];
