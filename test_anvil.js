import fs from 'fs'
import Anvil from '@anvilco/anvil'
import dotenv from 'dotenv'

dotenv.config()

const pdfTemplateID = '7VCXZAolDIPToVLh3O3O'
const apiKey = process.env.ANVIL_API_KEY

const exampleData = {
  title: 'My PDF Title',
  fontSize: 10,
  textColor: '#CC0000',
  data: {
    someFieldId: 'Hello World!',
  },
}

const anvilClient = new Anvil({ apiKey })
const { statusCode, data } = await anvilClient.fillPDF(
  pdfTemplateID,
  exampleData
)

console.log(statusCode) // => 200

// Data will be the filled PDF binary data
fs.writeFileSync('output.pdf', data, { encoding: null })

