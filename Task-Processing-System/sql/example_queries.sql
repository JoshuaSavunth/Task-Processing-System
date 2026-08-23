INSERT INTO jobs (type, input, status)
VALUES ('fibonacci', 40, 'PENDING')
RETURNING id;

SELECT id, type, input, status, result, error,
       created_at, started_at, completed_at
FROM jobs WHERE id = 1;

SELECT id, type, input
FROM jobs
WHERE status = 'PENDING'
ORDER BY created_at
FOR UPDATE SKIP LOCKED;

UPDATE jobs
SET status = 'COMPLETED', result = '102334155', completed_at = CURRENT_TIMESTAMP
WHERE id = 1;