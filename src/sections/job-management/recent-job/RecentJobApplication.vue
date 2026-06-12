<script setup lang="ts">
import VueApexCharts from "vue3-apexcharts";
// SHADCN COMPONENTS
import { Card, CardTitle } from "@/components/ui/card";
// CUSTOM COMPOSABLE
import { useChartOptions } from "./useChartOptions";

const { chartOptions, series } = useChartOptions();
</script>

<template>
  <Card class="px-5 pt-6 pb-2 col-span-full lg:col-span-6">
    <CardTitle>Recent Job Applications</CardTitle>
    <VueApexCharts type="bar" height="280" :options="chartOptions" :series="series" />
  </Card>
</template>
