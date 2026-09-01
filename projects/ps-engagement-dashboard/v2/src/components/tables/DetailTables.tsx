"use client";

import {
  Card,
  Table,
  TableHead,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  Badge,
} from "@tremor/react";

interface RiskTableProps {
  risks: { account: string; project: string; issue: string; action: string }[];
  loading?: boolean;
}

export function RiskTable({ risks, loading }: RiskTableProps) {
  if (loading) {
    return (
      <Card className="ring-0">
        <div className="animate-pulse space-y-3">
          <div className="h-4 w-48 bg-crystalline-border rounded" />
          <div className="h-32 bg-crystalline-border rounded" />
        </div>
      </Card>
    );
  }

  return (
    <Card className="ring-0">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-headline font-bold text-sm text-crystalline-text">
          Delivery Risk & Action
        </h3>
        <Badge color="red" size="sm">
          {risks.length} Red Accounts
        </Badge>
      </div>
      <Table>
        <TableHead>
          <TableRow>
            <TableHeaderCell className="text-crystalline-muted text-xs">Account</TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs">Project</TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs">Issue</TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs">Action</TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {risks.length === 0 ? (
            <TableRow>
              <TableCell colSpan={4}>
                <p className="text-crystalline-muted text-center py-4 text-sm">
                  No at-risk projects
                </p>
              </TableCell>
            </TableRow>
          ) : (
            risks.map((r, i) => (
              <TableRow key={i}>
                <TableCell className="text-xs font-medium">{r.account}</TableCell>
                <TableCell className="text-xs">{r.project}</TableCell>
                <TableCell className="text-xs">
                  <Badge color="red" size="xs">{r.issue}</Badge>
                </TableCell>
                <TableCell className="text-xs text-crystalline-primary font-medium">
                  {r.action}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </Card>
  );
}

interface DistrictTableProps {
  districts: {
    district: string;
    engagedPct: number;
    eacv: number;
    ucCount: number;
    totalUcs: number;
  }[];
  loading?: boolean;
}

export function DistrictTable({ districts, loading }: DistrictTableProps) {
  if (loading) {
    return (
      <Card className="ring-0">
        <div className="animate-pulse space-y-3">
          <div className="h-4 w-48 bg-crystalline-border rounded" />
          <div className="h-32 bg-crystalline-border rounded" />
        </div>
      </Card>
    );
  }

  return (
    <Card className="ring-0">
      <h3 className="font-headline font-bold text-sm text-crystalline-text mb-4">
        District Breakdown
      </h3>
      <Table>
        <TableHead>
          <TableRow>
            <TableHeaderCell className="text-crystalline-muted text-xs">District</TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs">Active PS Projects</TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs">PS-Engaged UCs</TableHeaderCell>
            <TableHeaderCell className="text-crystalline-muted text-xs">EACV</TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {districts.map((d, i) => (
            <TableRow key={i}>
              <TableCell className="text-xs font-medium">{d.district}</TableCell>
              <TableCell className="text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1.5 bg-crystalline-border rounded-full overflow-hidden">
                    <div
                      className="h-full bg-crystalline-primary rounded-full"
                      style={{ width: `${Math.min(d.engagedPct * 100, 100)}%` }}
                    />
                  </div>
                  <span>{(d.engagedPct * 100).toFixed(0)}% Engaged</span>
                </div>
              </TableCell>
              <TableCell className="text-xs">{d.ucCount} UCs</TableCell>
              <TableCell className="text-xs font-medium">
                ${(d.eacv / 1_000_000).toFixed(1)}M
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}
