<script setup lang="ts">
// SHADCN COMPONENTS
import {
  Table,
  TableRow,
  TableCell,
  TableBody,
  TableHead,
  TableHeader
} from "@/components/ui/table";
import { Card } from "@/components/ui/card";
import { Badge, BadgeVariants } from "@/components/ui/badge";

const getBadgeVariant = (status: string): BadgeVariants["variant"] => {
  const str = status.toLowerCase();
  if (str === "verified") return "default";
  else if (str === "waiting") return "success";
  else if (str === "hidden") return "secondary";
  else if (str === "rejected") return "destructive";
};

const tableHeads = ["Name", "Email", "Status"];

const rows = [
  { id: 1, name: "Olivia Rhye", email: "olivia@example.com", status: "Verified" },
  { id: 2, name: "Phoenix Baker", email: "phoenix@example.com", status: "Waiting" },
  { id: 3, name: "Lana Steiner", email: "lana@example.com", status: "Verified" },
  { id: 4, name: "Demi Wilkinson", email: "demi@example.com", status: "Hidden" },
  { id: 5, name: "Candice Wu", email: "candice@example.com", status: "Rejected" }
];
</script>

<template>
  <Card class="mb-6">
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead :key="head" v-for="head in tableHeads" class="py-5">{{ head }}</TableHead>
        </TableRow>
      </TableHeader>

      <TableBody>
        <TableRow
          :key="row.id"
          v-for="row in rows"
          class="[&>td]:font-normal [&>td]:border-b [&>td]:border-border">
          <TableCell class="font-medium">{{ row.name }}</TableCell>
          <TableCell>{{ row.email }}</TableCell>
          <TableCell>
            <Badge :variant="getBadgeVariant(row.status)">{{ row.status }}</Badge>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </Card>
</template>
