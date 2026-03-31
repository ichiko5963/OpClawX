
import { Mastra } from '@mastra/core/mastra';
import { PinoLogger } from '@mastra/loggers';
import { LibSQLStore } from '@mastra/libsql';
import { weatherWorkflow } from './workflows/weather-workflow';
import { weatherAgent } from './agents/weather-agent';
import { searchAgent } from './agents/search-agent';
import { esRagAgent } from './agents/es-rag-agent';
import { advancedEsRagAgent } from './agents/advanced-es-rag-agent';
import { ragAnalysisAgent } from './agents/rag-analysis-agent';

export const mastra = new Mastra({
  workflows: { weatherWorkflow },
  agents: { weatherAgent, searchAgent, esRagAgent, advancedEsRagAgent, ragAnalysisAgent },
  storage: new LibSQLStore({
    // stores telemetry, evals, ... into memory storage, if it needs to persist, change to file:../mastra.db
    url: ":memory:",
  }),
  logger: new PinoLogger({
    name: 'Mastra',
    level: 'info',
  }),
});
