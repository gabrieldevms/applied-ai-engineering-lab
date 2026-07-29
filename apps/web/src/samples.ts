export const sampleRequirement = `Como QA, preciso validar o saldo final por conta considerando depósitos e retiradas.`;

export const sampleDatabaseSchema = {
  name: "qa_database",
  description: "Database used for QA validation.",
  tables: [
    {
      name: "transactions",
      description: "Financial transactions.",
      columns: [
        {
          name: "transaction_id",
          data_type: "integer",
          nullable: false,
          primary_key: true,
        },
        {
          name: "account_id",
          data_type: "integer",
          nullable: false,
        },
        {
          name: "amount",
          data_type: "decimal",
          nullable: false,
        },
        {
          name: "transaction_type",
          data_type: "varchar",
          nullable: false,
        },
      ],
    },
  ],
};

export const sampleTableData = [
  {
    table_name: "transactions",
    rows: [
      {
        transaction_id: 123,
        account_id: 101,
        amount: 10.0,
        transaction_type: "Deposit",
      },
      {
        transaction_id: 124,
        account_id: 101,
        amount: 20.0,
        transaction_type: "Deposit",
      },
      {
        transaction_id: 125,
        account_id: 101,
        amount: 5.0,
        transaction_type: "Withdrawal",
      },
      {
        transaction_id: 126,
        account_id: 201,
        amount: 20.0,
        transaction_type: "Deposit",
      },
      {
        transaction_id: 128,
        account_id: 201,
        amount: 10.0,
        transaction_type: "Withdrawal",
      },
    ],
  },
];

export const sampleSqlRegressionSuite = {
  suite_name: "local-data-analysis-regression",
  metadata: {
    environment: "local-web-console",
  },
  scenarios: [
    {
      scenario_id: "final-account-balance",
      name: "Final account balance",
      description:
        "Validate final account balance by account using deposits and withdrawals.",
      request: {
        question: "Qual é o saldo final por conta?",
        language: "pt-BR",
        max_rows: 100,
        database_schema: sampleDatabaseSchema,
        table_data: sampleTableData,
      },
      expected_result: {
        expected_status: "executed",
        expected_row_count: 2,
        expected_columns: ["account_id", "final_balance"],
        expected_rows: [
          {
            account_id: 101,
            final_balance: 25.0,
          },
          {
            account_id: 201,
            final_balance: 10.0,
          },
        ],
      },
    },
  ],
};
