require 'active_support/core_ext/string'

module Jekyll
  class UserIndexGenerator < Generator
    safe true

    def generate(site)
      audio_data = site.data['audio_data']['users']

      audio_data.each do |user, entries|
        # Generate the user index page
        site.pages << UserIndexPage.new(site, site.source, user, entries)
      end
    end
  end

  # Page for user's index (lists all audio entries)
  class UserIndexPage < Page
    def initialize(site, base, user, entries)
      @site = site
      @base = base
      @dir = File.join('u', user) # makes /u/username/index.html
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(base, '_layouts'), 'userprofile.html')

      # Pass entries to the page's data
      self.data['user'] = user
      self.data['entries'] = entries
    end
  end
end
