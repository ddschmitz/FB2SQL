# How many messages everyone has sent
Select DISTINCT P.Name, COUNT(*)
FROM Message AS M
INNER JOIN Participant AS P ON M.SenderID = P.ID
GROUP BY M.SenderID

# Last thing a person said
SELECT P.Name, M.Timestamp, M.Content
FROM Message AS M
INNER JOIN Participant AS P ON M.SenderID = P.ID
WHERE P.Name = "John Doe"
ORDER BY M.Timestamp DESC
LIMIT 1

# Number of posts each day
Select DISTINCT DATE(M.Timestamp), COUNT(*)
FROM Message AS M
INNER JOIN Participant AS P ON M.SenderID = P.ID
WHERE P.Name = "John Doe"
GROUP BY DATE(M.Timestamp)

# Number of reactions to each participants messages
Select DISTINCT P.Name, COUNT(R.ID)
FROM Message AS M
INNER JOIN Participant AS P ON M.SenderID = P.ID
INNER JOIN Reaction AS R ON M.ID = R.MessageID
GROUP BY M.SenderID
ORDER BY COUNT(R.ID)
