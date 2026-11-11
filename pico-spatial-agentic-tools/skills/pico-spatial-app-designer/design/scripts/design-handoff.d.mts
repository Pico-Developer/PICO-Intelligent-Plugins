export interface DesignHandoffIssue {
  level: 'error';
  code: string;
  path: string;
  message: string;
}

interface AssetCheckInput {
  spec: unknown;
  projectRoot: string;
  specPath: string;
  assetRoot?: string;
}

export function checkDesignAssets(input: AssetCheckInput): Promise<DesignHandoffIssue[]>;
export function checkDesignHandoff(
  input: AssetCheckInput & { preview?: string },
): Promise<DesignHandoffIssue[]>;
