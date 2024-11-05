/** @odoo-module **/
import { WebClient } from '@web/webclient/webclient'
import { patch } from '@web/core/utils/patch'
import { useService } from '@web/core/utils/hooks'

patch(WebClient.prototype, {
  async setup() {
    super.setup()
    const titleService = useService('title')
    this.orm = useService('orm')

    try {
      // Fetch the current company data
      const result = await this.orm.searchRead(
        'res.company',
        [['id', '=', this.env.services.company.currentCompany.id]],
        ['browser_title']
      )
      // Extract the browser title from the result
      const [{ browser_title: browserTitle }] = result

      // Set the browser title
      titleService.setParts({ zopenerp: browserTitle || 'Odoo' })
    } catch (error) {
      console.error('Failed to fetch company data:', error)
      titleService.setParts({ zopenerp: 'Odoo' })
    }
  }
})
