const generateRunId = (): string => {
  const result = [];
  const characters = '0123456789';
  const charactersLength = characters.length;
  for (let i = 0; i < 40; i += 1) {
    result.push(characters.charAt(Math.floor(Math.random()
                  * charactersLength)));
  }
  return result.join('');
};

export default generateRunId;